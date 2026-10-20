#!/usr/bin/env python3
"""Replay changed result nodes and their dependents using saved app parameters."""
import argparse
import hashlib
import json
from pathlib import Path
from run_simulation import run_simulation


def file_references(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == 'file' and isinstance(child, str) and not child.startswith('@'):
                yield child
            else:
                yield from file_references(child)
    elif isinstance(value, list):
        for child in value:
            yield from file_references(child)


def replay_order(dependencies, seeds):
    missing = set(seeds) - dependencies.keys()
    if missing:
        raise ValueError(f'unknown changed results: {sorted(missing)}')
    affected = set(seeds)
    while True:
        expanded = affected | {name for name, deps in dependencies.items() if deps & affected}
        if expanded == affected:
            break
        affected = expanded
    order, visiting, visited = [], set(), set()
    def visit(name):
        if name in visiting:
            raise ValueError(f'result dependency cycle at {name}')
        if name in visited:
            return
        visiting.add(name)
        for dep in sorted(dependencies[name] & affected):
            visit(dep)
        visiting.remove(name)
        visited.add(name)
        order.append(name)
    for name in sorted(affected):
        visit(name)
    return order


def replay(folder, seeds, manifest, resume=False):
    folder = Path(folder).resolve()
    manifest = Path(manifest)
    old = json.loads(manifest.read_text()) if resume and manifest.exists() else {'completed': {}}
    params = {p.name.removesuffix('.params.json'): p for p in folder.glob('*.params.json')}
    result_paths = {(folder / f'{name}.json').resolve(): name for name in params}
    dependencies, apps = {}, {}
    for name, path in params.items():
        record = json.loads(path.read_text())
        refs = [(path.parent / x).resolve() for x in file_references(record)]
        dependencies[name] = {result_paths[x] for x in refs if x in result_paths}
        output = folder / f'{name}.json'
        apps[name] = json.loads(output.read_text())['simulation'] if output.exists() else old.get('applications', {}).get(name)
        if not apps[name]:
            raise ValueError(f'no application identity for result {name}')
    order = replay_order(dependencies, seeds)
    state = {'order': order, 'changed': seeds, 'applications': apps, 'completed': old['completed']}
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(state, indent=2)+'\n')
    root=Path(__file__).resolve().parents[1]/'simulations'
    code=hashlib.sha256()
    for path in sorted((root/'_common').glob('*.py'))+sorted(root.glob('*/run.py')):
        code.update(path.name.encode());code.update(path.read_bytes())
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    for name in order:
        path = params[name]
        fingerprint = {'parameters': digest(path), 'implementation': code.hexdigest(), 'dependencies': {dep: digest(folder / f'{dep}.json') for dep in sorted(dependencies[name])}}
        prior = state['completed'].get(name, {})
        if resume and (folder / f'{name}.json').exists() and prior.get('fingerprint') == fingerprint and prior.get('result_sha256') == digest(folder / f'{name}.json'):
            print(name, 'already replayed', flush=True)
            continue
        print(name, 'running', apps[name], flush=True)
        document = run_simulation(apps[name], path, folder, name)
        state['completed'][name] = {'fingerprint': fingerprint, 'result_sha256': digest(folder / f'{name}.json'), 'implementation_sha256': document['implementation_sha256'], 'simulation': apps[name]}
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps(state, indent=2)+'\n')
        print(name, 'computed', flush=True)
    return state


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--folder', required=True)
    parser.add_argument('--changed', nargs='+', required=True)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    replay(args.folder, args.changed, args.manifest, args.resume)
