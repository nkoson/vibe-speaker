"""Normalization, domain, geometry and field-model limiting cases."""
import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"simulations"))
from _common import cli,acoustics,geometry,apps,radiation

def test_delayed_complex_interpolation_preserves_unit_amplitude():
    f=np.array([100.,200.]);target=np.array([120.,141.421356,190.]);delay=.005
    actual=cli.interp_complex(target,f,np.exp(-2j*np.pi*f*delay),delay_s=delay)
    np.testing.assert_allclose(actual,np.exp(-2j*np.pi*target*delay),atol=1e-12)

def test_source_magnitude_only_phase_provenance(tmp_path):
    p,basis=apps.module("source_response")._pressure({"acoustic":{"kind":"measured","frequency_hz":[100,200],"spl_db":[90,90]}},np.array([100,200]),tmp_path)
    assert "reconstructed" in basis and "measured complex" not in basis

def test_reference_domain_diagnostics_and_explicit_zero(tmp_path):
    cli.write_document(tmp_path/"source.json",{"results":{"f_hz":[10,100],"curve":[1,2]}})
    token=cli.REFERENCE_DIAGNOSTICS.set([])
    spec={"file":"source.json","path":"results.curve","extrapolation":"zero"}
    actual=cli.curve_from_reference(spec,tmp_path,[5,50,200],"real")
    assert actual[0]==actual[2]==0
    assert cli.REFERENCE_DIAGNOSTICS.get()[0]["extrapolated_points"]==2
    with pytest.raises(cli.InputError):cli.curve_from_reference(dict(spec,extrapolation="error"),tmp_path,[5,50],"real")
    cli.REFERENCE_DIAGNOSTICS.reset(token)

def test_box_mesh_volume_normals_and_transformed_containment():
    shape={"shape":"box","dimensions_m":[1,2,3],"rotation_deg":[0,0,90],"origin_m":[2,0,0]}
    mesh=geometry.object_mesh(shape)
    assert mesh["signed_volume_m3"]==pytest.approx(6)
    assert mesh["boundary_edges"]==mesh["inconsistent_edges"]==0
    assert geometry.contains(shape,[[1, .5,1]])[0]

def test_air_union_subtracts_overlap_once(tmp_path):
    assembly={"objects":[{"id":"air","role":"air","dimensions_m":[1,1,1]},
                          {"id":"a","dimensions_m":[.5,1,1]},
                          {"id":"b","origin_m":[.25,0,0],"dimensions_m":[.5,1,1]}]}
    result=apps.module("assembly_geometry").compute({"assembly":assembly,"cell_sizes_m":[.25,.125]},tmp_path)
    assert result["volume_refinement"][-1]["air_volume_m3"]==pytest.approx(.25)
    assert result["solid_intersections"][0]["intersection_m3"]==pytest.approx(.25)

def test_exterior_sphere_matches_pulsating_sphere_and_refines():
    f=np.array([100.]);radius=.1;omega=2*np.pi*f;k=omega/cli.C
    exact=1j*omega*cli.RHO*radius/(1+1j*k*radius)*radius*np.exp(-1j*k*(1-radius))
    errors=[]
    for level in (1,2):
        mesh=geometry.object_mesh({"shape":"sphere","radius_m":radius,"subdivisions":level})
        p,_,res,_=apps.module("exterior_bem").solve(mesh,f,np.ones((1,len(mesh["areas"]))),[[0,1,0]])
        errors.append(abs(p[0,0]/exact[0]-1))
        assert max(res)<1e-12
    assert errors[1]<errors[0]
    assert errors[1]<.12

def test_modal_room_reciprocity_and_uniform_compliance(tmp_path):
    params={"frequencies":{"values_hz":[.1,.2]},"room":{"dimensions_m":[4,5,3]},"mode_order":2,
            "sources":[{"position_m":[1,1,1],"volume_velocity_m3_s":1e-4}],"receivers_m":[[2,3,1]]}
    result=apps.module("room_modal").compute(params,tmp_path)
    expected=-1j*cli.RHO*cli.C**2*1e-4/(2*np.pi*np.array([.1,.2])*60)
    np.testing.assert_allclose(result["pressure_pa"][0],expected,rtol=.001)
    params["sources"][0]["position_m"],params["receivers_m"][0]=params["receivers_m"][0],params["sources"][0]["position_m"]
    other=apps.module("room_modal").compute(params,tmp_path)
    np.testing.assert_allclose(result["pressure_pa"],other["pressure_pa"],atol=1e-12)

def test_signed_dipole_and_cardioid_patterns():
    angles=np.deg2rad(np.array([0,90,180]))
    np.testing.assert_allclose(acoustics.directivity({"kind":"dipole"},1000,angles,0),[1,0,-1],atol=1e-12)
    np.testing.assert_allclose(acoustics.directivity({"kind":"cardioid"},1000,angles,0),[1,.5,0],atol=1e-12)

def test_mutual_coils_conserve_power_and_transform_voltage(tmp_path):
    network=dict(frequencies={"values_hz":[500,1000]},components=[],
                 transformers=[dict(id="T",primary_nodes=["in","0"],secondary_nodes=["out","g"],
                                    primary_inductance_mh=1000,turns_ratio=2,coupling=.9999,primary_dcr_ohm=.01,secondary_dcr_ohm=.01)],
                 sources=[dict(id="amp",plus="in",minus="0",voltage_rms=1)],
                 loads=[dict(id="load",plus="out",minus="g",impedance={"kind":"resistive","r_ohm":100})])
    result=apps.module("board_nodal").compute(network,tmp_path)["modes"][0]
    np.testing.assert_allclose(abs(result["loads"][0]["transfer"]),.5,rtol=.002)
    assert result["power_relative_residual"]<1e-9

def test_coupled_cabinet_zero_coupling_and_spatial_symmetry(tmp_path):
    import json,copy
    path=Path(__file__).resolve().parents[1]/"simulations/coupled_cabinet/example.json"
    params=json.loads(path.read_text());params["coupling_scale"]=0
    result=apps.module("coupled_cabinet").compute(params,tmp_path)
    np.testing.assert_allclose(result["panel_displacement_m"],0,atol=1e-16)
    params["coupling_scale"]=1
    result=apps.module("coupled_cabinet").compute(params,tmp_path)
    assert np.max(abs(result["panel_displacement_m"]))>0
    assert max(result["relative_residual"])<1e-8

def test_rays_transport_power_and_zero_absorbing_reflection(tmp_path):
    p=dict(room_surface={"shape":"box","dimensions_m":[4,5,3]},source_position_m=[1,1,1],
           receivers_m=[[2,3,1]],rays=30,max_bounces=3,energy_absorption=1,scattering=0)
    result=apps.module("room_rays").compute(p,tmp_path)
    np.testing.assert_allclose(result["reflected_mean_square_pa2"],0)
    expected=4*np.pi/(cli.RHO*cli.C)
    np.testing.assert_allclose(result["transport"]["absorbed_power_w"]+result["transport"]["remaining_power_w"],expected)

def test_nonlinear_energy_accounting_and_small_signal(tmp_path):
    import json
    p=json.loads((Path(__file__).resolve().parents[1]/"simulations/nonlinear_driver/example.json").read_text())
    p["sample_rate_hz"]=20000
    result=apps.module("nonlinear_driver").compute(p,tmp_path)
    balance=result["energy_balance"]
    assert abs(balance["residual_j"])<max(abs(balance["stored_change_j"])*.005,1e-8)
    assert np.max(result["coil_temperature_c"])>=20
    p["drive"]["tones"][0]["voltage_rms"]*=.1
    small=apps.module("nonlinear_driver").compute(p,tmp_path)
    np.testing.assert_allclose(result["displacement_m"]*.1,small["displacement_m"],atol=1e-8,rtol=.01)

def test_thermal_fixed_point_residual_and_no_drive_limit(tmp_path):
    import json
    p=json.loads((Path(__file__).resolve().parents[1]/"simulations/electrothermal_network/example.json").read_text())
    p["iterations"]=50
    result=apps.module("electrothermal_network").compute(p,tmp_path)
    assert np.max(abs(result["iterations"][-1]["heat_balance_temperature_residual_k"]))<1e-6
    p["programme"]["voltage_rms"]=0
    cold=apps.module("electrothermal_network").compute(p,tmp_path)
    assert cold["sections"][0]["coil_temperature_c"]==20

def test_general_network_fit_known_resistor_and_actual_stock(tmp_path):
    import json
    p=json.loads((Path(__file__).resolve().parents[1]/"simulations/network_fit/example.json").read_text())
    result=apps.module("network_fit").compute(p,tmp_path)
    minimum=result["trials"][result["numerical_minimum_index"]]
    assert minimum["values"][0]==pytest.approx(8,rel=1e-4)
    assert len(result["stock_trials"])==2

def test_scenario_draws_are_shared_and_nominal_is_replayed(tmp_path):
    import json
    p=json.loads((Path(__file__).resolve().parents[1]/"simulations/system_scenarios/example.json").read_text())
    p["model_scenarios"]=[{"name":"a"},{"name":"b"}]
    result=apps.module("system_scenarios").compute(p,tmp_path)
    a,b=result["outcomes"][:4],result["outcomes"][4:]
    assert [r["variables"] for r in a]==[r["variables"] for r in b]
    assert a[0]["observables"]["minimum_impedance"]==pytest.approx(12)

def test_room_pressure_feedback_changes_motor_motion(tmp_path):
    import json
    driver=json.loads((Path(__file__).resolve().parents[1]/"simulations/nonlinear_driver/example.json").read_text())["driver"]
    f=np.array([5.,10.]);e=acoustics.driver_elements(driver["ts"]);s=2j*np.pi*f
    free=e["bl"]/((e["re"]+s*e["le"])*(e["rms"]+s*e["mms"]+1/(s*e["cms"]))+e["bl"]**2)
    p=dict(frequencies={"values_hz":f.tolist()},room={"dimensions_m":[1,1,1]},mode_order=2,
           sources=[dict(position_m=[.5,.5,.5],radius_m=.1,driver=driver,voltage_rms=1)],receivers_m=[[.7,.6,.5]])
    result=apps.module("room_modal").compute(p,tmp_path)
    actual=np.array([r[0]["volume_velocity_m3_s"] for r in result["motor_states"]])/e["sd"]
    assert np.all(abs(actual)<abs(free))

def test_cavity_canonical_source_independent_of_stress_drive(tmp_path):
    import json,copy
    root=Path(__file__).resolve().parents[1]/"simulations"
    p=json.loads((root/"cavity_modes/example.json").read_text())
    p["method"]={"kind":"rectangular","max_mode_hz":500}
    p["frequencies"]={"values_hz":[20,100,300,500]}
    p["drive"]={"voltage_rms":1,"series_resistance_ohm":0}
    a=apps.module("cavity_modes").compute(p,tmp_path)
    p["drive"]={"voltage_rms":10,"series_resistance_ohm":2}
    b=apps.module("cavity_modes").compute(p,tmp_path)
    np.testing.assert_allclose(a["pressure_per_volt_pa"],b["pressure_per_volt_pa"])
    np.testing.assert_allclose(a["z_ohm"],b["z_ohm"])

def test_global_network_fit_retains_incumbent_under_budget(tmp_path):
    import json
    p=json.loads((Path(__file__).resolve().parents[1]/"simulations/network_fit/example.json").read_text())
    p.update(optimizer="differential_evolution",max_evaluations=12,seed=3)
    result=apps.module("network_fit").compute(p,tmp_path)
    assert result["trials"][result["numerical_minimum_index"]]["cost"]<=result["trials"][0]["cost"]

def test_stock_constraint_is_a_numeric_margin_not_design_verdict(tmp_path):
    import json
    p=json.loads((Path(__file__).resolve().parents[1]/"simulations/network_fit/example.json").read_text())
    p["constraints"]=[dict(quantity="terminal_voltage_rms",load_id="driver",maximum=.4)]
    result=apps.module("network_fit").compute(p,tmp_path)
    row=result["trials"][result["numerical_minimum_index"]]
    assert row["constraint_margins"][0]>=-1e-6
    assert row["values"][0]==pytest.approx(12,rel=1e-3)
    assert not any(key in row for key in ("pass","fail","acceptable","verdict"))

def test_shared_assembly_maps_source_normal_and_position(tmp_path):
    cli.write_document(tmp_path/"source.json",dict(results=dict(f_hz=[100,200],pressure_per_volt_pa=np.ones(2,complex),acoustic_depth_mm=0,directivity={"kind":"omni"})))
    params=dict(assembly=dict(objects=[dict(id="baffle",dimensions_m=[1,1,1],origin_m=[1,2,0],rotation_deg=[0,0,-90])],
                             sources=[dict(id="driver",object_id="baffle",local_position_m=[0,0,.5],local_normal=[0,1,0])]),
                sections=[dict(name="driver",source={"file":"source.json"},assembly_source="driver")])
    section=radiation.load_sections(params,np.array([100,200]),tmp_path)[0]
    np.testing.assert_allclose(section["centre"],[1,2,.5])
    np.testing.assert_allclose(section["axis"],[1,0,0],atol=1e-12)

def test_common_observer_phase_reproduces_supplied_field_once(tmp_path):
    f=np.array([100.,200.]);observer=np.array([0.,3.,1.]);centre=np.array([0.,0.,.3])
    distance=np.linalg.norm(observer-centre)
    original=np.exp(-2j*np.pi*f*distance/cli.C)/distance
    params=dict(frequencies={"values_hz":f.tolist()},acoustic=dict(kind="measured",frequency_hz=f.tolist(),
        real_pa=original.real.tolist(),imag_pa=original.imag.tolist(),voltage_rms=1,distance_m=3,
        contract=dict(phase_reference="common_observer",reference_distance_m=3,observer_position_m=observer.tolist())),
        impedance=dict(kind="resistive",r_ohm=8),directivity=dict(kind="omni"))
    result=apps.module("source_response").compute(params,tmp_path)
    cli.write_document(tmp_path/"field.json",dict(status="computed",results=result))
    system=dict(sections=[dict(name="source",source={"file":"field.json"},position={"z_mm":300})])
    sections=radiation.load_sections(system,f,tmp_path)
    pressure,_=radiation.pressure(sections,f,[observer],3)
    np.testing.assert_allclose(pressure[0],original*3*np.exp(2j*np.pi*f*3/cli.C),atol=1e-12)
    wrapped=apps.module("source_response").compute(dict(frequencies={"values_hz":f.tolist()},
        acoustic=dict(kind="simulation",reference={"file":"field.json"}),
        impedance=dict(kind="resistive",r_ohm=8)),tmp_path)
    np.testing.assert_allclose(wrapped["pressure_per_volt_pa"],result["pressure_per_volt_pa"],atol=1e-12)

def test_dipole_ray_power_integrates_to_one_third_omni(tmp_path):
    p=dict(room_surface={"shape":"box","dimensions_m":[4,5,3]},source_position_m=[1,1,1],
           receivers_m=[[2,3,1]],rays=300,max_bounces=0,energy_absorption=1,scattering=0,
           directivity={"kind":"dipole"},source_normal=[0,0,1])
    result=apps.module("room_rays").compute(p,tmp_path)
    np.testing.assert_allclose(result["transport"]["launched_power_w"],4*np.pi/(3*cli.RHO*cli.C),rtol=1e-4)

def test_rotational_restraint_converges_toward_clamped_plate_reference(tmp_path):
    import json
    reference=json.loads((Path(__file__).resolve().parents[1]/"benchmarks/clamped-square-reference.json").read_text())["values"][0]
    material=dict(thickness_m=.01,density_kg_m3=1000,youngs_modulus_pa=1e9,poisson_ratio=.3,
                  edge_rotational_stiffness=dict(u_min=1e8,u_max=1e8,v_min=1e8,v_max=1e8))
    p=dict(frequencies={"values_hz":[10,20]},cabinet=dict(dimensions_m=[1,1,1],material=material),
           acoustic_mode_order=1,surface_divisions=1,source=dict(position_m=[.5,.5,.5],volume_velocity_m3_s=0),
           exterior_feedback=False,coupling_scale=0)
    scale=np.sqrt((1e9*.01**3/(12*(1-.3**2)))/(1000*.01))
    errors=[]
    for order in (3,5,7):
        p["panel_mode_order"]=order
        result=apps.module("coupled_cabinet").compute(p,tmp_path)
        value=result["mechanical_modes_hz"][0]*2*np.pi/scale
        errors.append(value-reference)
    # Ritz basis approaches the clamped result from above; coarse modes do not
    # acquire clamped accuracy merely because the spring is extremely stiff.
    assert errors[0]>errors[1]>errors[2]>0

def test_network_fit_curve_target_matches_constant_target(tmp_path):
    import json,copy
    root=Path(__file__).resolve().parents[1]/'simulations'
    p=json.loads((root/'network_fit/example.json').read_text())
    p['max_evaluations']=1
    p['system']={'cabinet':{},'observer':{'distance_m':3,'ear_height_m':1},'sections':[
        {'name':'test','load_id':p['network']['loads'][0]['id'],'source':{'file':'source.json'},'position':{'x_mm':0,'z_mm':1000}}]}
    source=apps.module('source_response').compute({'acoustic':{'kind':'bandwidth_prior','sensitivity_db_2v83_1m':90},'impedance':{'kind':'resistive','r_ohm':8},'frequencies':{'min_hz':20,'max_hz':20000,'points':100}},tmp_path)
    cli.write_document(tmp_path/'source.json',{'results':source})
    p['target']={'spl_db':90,'band_hz':[100,10000],'weights':[{'band_hz':[100,500],'weight':2}]}
    p['constraints']=[{'quantity':'acoustic_relative_db','band_hz':[100,1000],'reference_band_hz':[300,3000],'minimum':-3}]
    a=apps.module('network_fit').compute(p,tmp_path)
    cli.write_document(tmp_path/'target.json',{'f_hz':[20,20000],'db':[90,90]})
    p['target']['spl_db']={'file':'target.json','frequency_path':'f_hz','path':'db'}
    b=apps.module('network_fit').compute(p,tmp_path)
    assert a['trials'][0]['cost']==pytest.approx(b['trials'][0]['cost'],rel=1e-12)
    f=np.asarray(a['f_hz']);curve=a['trials'][0]['acoustic_spl_db'][0]
    expected=np.min(curve[(f>=100)&(f<=1000)]-np.mean(curve[(f>=300)&(f<=3000)]))+3
    assert a['trials'][0]['constraint_margins'][0]==pytest.approx(expected)
