"""Port transfer limits and source ownership, independent of any project selection."""
import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'simulations'))
from _common import apps,acoustics,cli

def test_uniform_segments_equal_closed_form_and_conserve_reciprocity():
    app=apps.module('cavity_modes');f=np.geomspace(10,1500,100)
    port={'inner_diameter_mm':100,'length_mm':180,'inner_end_correction_mm':0,
          'segments':[{'length_mm':30,'diameter_mm':100}]*6}
    a,b,c,d,z,_=app.port_transfer(port,f,2,35,20)
    gamma=2*np.pi*35/(cli.C*20)+2j*np.pi*f/cli.C;zc=cli.RHO*cli.C/(2*np.pi*.05**2)
    np.testing.assert_allclose(a,np.cosh(gamma*.180),rtol=1e-12)
    np.testing.assert_allclose(b,zc*np.sinh(gamma*.180),rtol=1e-12)
    np.testing.assert_allclose(c,np.sinh(gamma*.180)/zc,rtol=1e-12)
    np.testing.assert_allclose(a*d-b*c,1,atol=1e-12)

def test_taper_low_frequency_mass_and_parallel_port_scaling():
    app=apps.module('cavity_modes');f=np.array([.01]);segs=[{'length_mm':40,'diameter_mm':140},{'length_mm':100,'diameter_mm':100},{'length_mm':40,'diameter_mm':140}]
    port={'inner_diameter_mm':100,'length_mm':180,'inner_end_correction_mm':0,'outer_mouth_diameter_mm':140,'segments':segs}
    r=app.port_transfer(port,f,2,35,1e15);mass=sum(cli.RHO*v['length_mm']/1000/(2*np.pi*(v['diameter_mm']/2000)**2) for v in segs)
    assert (r[1][0].imag/(2*np.pi*f[0]))==pytest.approx(mass,rel=1e-8)
    single=app.port_transfer(port,f,1,35,1e15)
    assert r[1][0]==pytest.approx(single[1][0]/2)
    assert r[4][0]==pytest.approx(single[4][0]/2)

def test_explicit_inner_end_mass_and_no_silent_length_mismatch():
    app=apps.module('cavity_modes');f=np.array([.01]);p={'inner_diameter_mm':100,'length_mm':100,'inner_end_correction_mm':0}
    base=app.port_transfer(p,f,1,35,1e15);corrected=app.port_transfer(dict(p,inner_end_correction_mm=30),f,1,35,1e15)
    diff=(corrected[1]-base[1]).imag/(2*np.pi*f)
    np.testing.assert_allclose(diff,cli.RHO*.03/(np.pi*.05**2),rtol=1e-8)
    with pytest.raises(ValueError,match='sum'):app.port_transfer(dict(p,segments=[{'length_mm':90,'diameter_mm':100}]),f,1,35,20)

def test_zero_mode_recovers_leaky_lumped_box_at_low_frequency(tmp_path):
    app=apps.module('cavity_modes');f=np.geomspace(5,40,120);V=50;D=40;L=100;N=2
    fb=cli.C/(2*np.pi)*np.sqrt(N*np.pi*(D/2000)**2/(V/1000*(L+.732*D)/1000))
    ts=dict(fs_hz=35,vas_l=80,qms=6,qes=.4,re_ohm=5.5,sd_cm2=220,le_mh=.5)
    p=dict(cavity=dict(width_mm=400,depth_mm=250,height_mm=500),driver=dict(ts=ts,position=dict(x_mm=200,z_mm=250)),
           outlet=dict(type='port',positions=[dict(face='rear',x_mm=100,z_mm=100),dict(face='rear',x_mm=300,z_mm=100)],inner_diameter_mm=D,length_mm=L),
           enclosure=dict(type='vented',net_volume_l=V,tuning_hz=fb,ql=7,qp=30,port=dict(diameter_mm=D,count=N)),drive=dict(voltage_rms=2.83),_base_dir=tmp_path)
    g=app._geometry(p);basis=app.rectangular_modes(g,1)
    actual=app.acoustic_response(g,p,basis,f,False)
    lumped=acoustics.box_response(ts,p['enclosure'],f,2.83,0,'half')
    np.testing.assert_allclose(actual['excursion_peak_mm'],lumped['excursion_peak_mm'],rtol=.025)
    # This QL change must affect the vented result; silently ignoring leakage is a regression.
    p['enclosure']['ql']=50
    low_loss=app.acoustic_response(g,p,basis,f,False)
    assert np.max(abs(actual['excursion_peak_mm']-low_loss['excursion_peak_mm']))>.01
