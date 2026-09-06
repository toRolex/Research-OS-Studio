"""One workflow per CLI call; CPU execution and typed mathematical handoff."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tests.test_walking_skeleton import run_cli, write_json
from research_os.workflows.mathematical import create_statement_candidate, confirm_statement

ROOT = Path(__file__).resolve().parents[2]


class WorkflowCLIIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.test')

    def git(self, *args):
        return subprocess.check_output(['git','-C',str(self.root),*args], stderr=subprocess.PIPE, text=True).strip()

    def pin(self, name):
        self.git('add','.')
        self.git('commit','--allow-empty','-qm','fixture')
        return {'path': name, 'sha256': hashlib.sha256((self.root/name).read_bytes()).hexdigest(), 'commit': self.git('rev-parse','HEAD')}

    def invoke(self, name, request):
        write_json(self.root/'request.json', request)
        return run_cli(name,'--project',str(self.root),'--request','request.json')

    def test_cpu_design_prepare_run_analyze_are_separate_explicit_invocations(self):
        for name in ('experiment.py','data.json'):
            shutil.copy2(ROOT/'reference-projects/computational'/name, self.root/name)
        write_json(self.root/'question.json', {'contract':{'name':'research-os/artifact','version':'1.1.0'},
                   'target':{'kind':'git','path':'question.json'}, 'type':{'name':'research-question','version':'1.0.0'},
                   'spec':{'question':'Does the fixed CPU example reproduce?', 'boundaries':['local CPU']}})
        source = self.pin('question.json')
        def boundary(name, kind, spec):
            write_json(self.root/name, {'contract':{'name':'research-os/artifact','version':'1.1.0'},
                       'target':{'kind':'git','path':name},'type':{'name':kind,'version':'1.0.0'},'spec':spec})
            pin = self.pin(name)
            return {'target':{'kind':'git','path':name,'commit':pin['commit']},'sha256':pin['sha256']}
        project_ref = boundary('project.json','project', {'name':'CPU fixture','question':'Does it reproduce?',
                               'boundaries':['local CPU'], 'principals':[{'identity':'user','roles':['user','researcher']}]})
        workstream_ref = boundary('workstream.json','workstream', {'project':project_ref,'name':'CPU',
                                  'intent':'Test fixed criterion','state':'active'})
        request = dict(project_ref=project_ref, workstream_ref=workstream_ref, source=source['path'], source_sha256=source['sha256'], source_commit=source['commit'],
                       output='design.json', report='design-report.json', hypothesis='MSE equals 1.25',
                       dataset={'target':{'kind':'git','path':'data.json'}}, controls=['constant mean'],
                       metrics=[{'name':'mean_squared_error','target':1.25}], run_matrix=[{'name':'cpu'}],
                       success_criteria=['MSE equals 1.25'], failure_criteria=['missing result'], stop_criteria=['budget exhausted'],
                       budget={'seconds':30.0,'cost_usd':0.0,'tokens':0,'gpu_hours':0.0,'attempts':6,'rounds':6})
        result = self.invoke('design-experiment',request)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertFalse((self.root/'preparation.json').exists())
        design = self.pin('design.json')
        selected = {'design':'design.json','design_sha256':design['sha256'],'design_commit':design['commit']}
        result = self.invoke('prepare-experiment',{**selected,'output':'preparation.json','report':'prepare-report.json',
                    'ledger_directory':'runs/prepare','commands':[[sys.executable,'-c','pass']]})
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertFalse((self.root/'result.json').exists())
        prep = self.pin('preparation.json')
        result = self.invoke('run-experiment',{**selected,'preparation':'preparation.json','preparation_sha256':prep['sha256'],
                    'preparation_commit':prep['commit'],'output':'run.json','report':'run-report.json',
                    'ledger_directory':'runs/execute','commands':[[sys.executable,'experiment.py']], 'expected_result':'result.json'})
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertFalse((self.root/'analysis.json').exists())
        run = self.pin('run.json')
        result = self.invoke('analyze-experiment',{'run':'run.json','run_sha256':run['sha256'],'run_commit':run['commit'],
                    'output':'analysis.json','report':'analysis-report.json','analysis_candidate':{
                        'method':'fixed criterion comparison','findings':[{'MSE':1.25}],
                        'uncertainties':['fixture only'],'criterion_results':[{'criterion':'MSE','verdict':'pass'}]}})
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        analysis = self.pin('analysis.json')
        boundary('claim.json','claim', {'project':project_ref,'workstream':workstream_ref,
                  'statement':'The fixed CPU baseline MSE equals 1.25.', 'scope':'whole_subject',
                  'conditions':['fixed four-value dataset'], 'limitations':['fixture only']})
        claim = self.pin('claim.json')
        result = self.invoke('assess-result-to-claim', {'analysis':'analysis.json','analysis_sha256':analysis['sha256'],
                  'analysis_commit':analysis['commit'],'claim':'claim.json','claim_sha256':claim['sha256'],
                  'claim_commit':claim['commit'],'evidence_output':'evidence.json','assessment_output':'assessment-result.json',
                  'report':'assess-report.json','method':'fixed criterion comparison','conditions':['fixed four-value dataset'],
                  'scope':['/statement'],'verdict':'supports','limitations':['fixture only']})
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        evidence = json.loads((self.root/'evidence.json').read_bytes())
        self.assertEqual(evidence['relations'][0]['relation'],'supports')
        validation = run_cli('validate','--project',str(self.root),'evidence.json')
        self.assertEqual(validation.returncode,0,validation.stdout)
        self.assertFalse((self.root/'publications').exists())
        for name in ('design.json','preparation.json','run.json','analysis.json'):
            result=run_cli('validate','--project',str(self.root),name)
            self.assertEqual(result.returncode,0,result.stdout)

    def test_math_candidate_is_typed_and_stops_before_lean(self):
        statement = create_statement_candidate(revision=1, quantifiers=['for every natural n'],
                    hypotheses=[], domain='natural numbers', conclusion='n + 0 = n', rationale='fixture')
        statement = confirm_statement(statement, principal='project:user',
                    confirmation=f"CONFIRM STATEMENT r1 {statement['semantic_digest']}")
        artifact = {'contract': {'name':'research-os/artifact','version':'1.1.0'},
                    'target': {'kind':'git','path':'statement.json'},
                    'type': {'name':'mathematical-statement','version':'1.0.0'}, 'spec':statement}
        write_json(self.root/'statement.json',artifact)
        pin = self.pin('statement.json')
        result = self.invoke('math-proof', {'statement_input': {key:pin[key] for key in ('path','sha256')},
                    'output':'proof.json','report':'proof-report.json','actor_principal':'project:author',
                    'examples':[],'counterexamples':[], 'lemma_map':[{'id':'L1','statement':'right identity','depends_on':[],'status':'proved'}],
                    'attempts':[{'id':'A1','approach':'right identity','argument':'Nat.add_zero','outcome':'candidate-proof','gaps':[]}],
                    'max_attempts':1})
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertFalse((self.root/'formalization.json').exists())
        validation = run_cli('validate','--project',str(self.root),'proof.json')
        self.assertEqual(validation.returncode,0,validation.stdout)
        self.assertFalse(json.loads(result.stdout)['automatic_next_workflow'])

    def test_math_statement_pin_is_required_before_any_output(self):
        result = self.invoke('math-proof', {'statement_input': {'path':'missing.json','sha256':'a'*64},
                                          'output':'proof.json','report':'proof-report.json'})
        self.assertEqual(result.returncode,2,result.stdout)
        self.assertFalse((self.root/'proof.json').exists())

    def test_missing_remote_configuration_is_blocked_not_success(self):
        # Through the public remote adapter boundary; no transport is started.
        from research_os.remote import RemoteAdapter
        receipt = RemoteAdapter(self.root, None).probe()
        self.assertEqual(receipt.exit_code, 3)
        self.assertEqual(receipt.state, 'blocked')


if __name__=='__main__':
    unittest.main()
