"""Observe registered method boundaries without modifying locked scientific code."""
from backend.api.progress import emit
from backend.simulation.lammps_runner import engine_capabilities


def hypotheses(state):
    return [dict(id=h.id, title=h.title, mechanism=h.mechanism,
                 confidence=h.confidence, ai_execution_mode=h.ai_execution_mode.value,
                 prediction_pct=h.predicted_strain_recovery_pct) for h in state.hypotheses]


def proposals(state):
    return [dict(experiment_id=p.experiment_id, intervention=p.intervention.value,
                 target_hypothesis_id=p.target_hypothesis_id, utility_score=p.utility_score, estimated_cost_sec=p.estimated_cost_sec,
                 expected_information_gain=p.expected_information_gain, risk_penalty=p.risk_penalty,
                 rationale=p.rationale, matched_seeds=p.matched_seeds,
                 ai_execution_mode=p.ai_execution_mode.value) for p in state.proposed_experiments]


def receipt(state):
    for event in reversed(state.audit_log):
        record = event.get('provenance') or {}
        if record.get('telemetry'):
            return {key: record[key] for key in ['action', 'telemetry', 'request_hash', 'response_hash', 'belief_changes'] if key in record}
    return {}


def observed_class(base, job_id, live=False):
    class ObservedInvestigator(base):
        _console_context = None
        _console_call = 0

        def _event(self, phase, status, message, **data):
            emit(self.store, job_id, phase, status, message, **data)

        def _save(self, message, stage, **detail):
            super()._save(message, stage, **detail)
            record = detail.get('provenance') or {}
            # The live overlay first prepares deterministic candidates; those are
            # not a completed model response. Wait for the actual action receipt.
            confirmed = not live or bool(record.get('telemetry'))
            if stage == 'hypothesize' and confirmed:
                self._event('hypotheses', 'completed', 'Possible explanations generated',
                            hypotheses=hypotheses(self.state), ai_execution_mode=self.state.ai_execution_mode.value, receipt=receipt(self.state))
                if not live:
                    self._event('plan', 'started', 'Ranking registered tests')
            elif stage == 'plan' and confirmed:
                self._event('plan', 'completed', 'Registered tests ranked',
                            proposals=proposals(self.state), ai_execution_mode=self.state.ai_execution_mode.value, receipt=receipt(self.state))
            elif stage == 'data_availability':
                self._event('simulate', 'skipped', message, experiment_id=detail.get('experiment_id'))

        def hypothesize(self, case_id):
            public = self.store.public(case_id)
            baseline = public.baseline_simulation
            self._event('observe', 'completed', 'Original sample and recorded measurements loaded',
                        case_id=case_id, atom_count=public.atom_count,
                        baseline=dict(sim_id=baseline.sim_id, outcome=baseline.outcome.value,
                                      failure_strain=baseline.failure_strain, max_observed_strain=baseline.max_observed_strain,
                                      peak_stress=baseline.peak_stress, numerical_valid=baseline.numerical_check.is_valid,
                                      engine_used=baseline.engine_used),
                        source='STORED_IMMUTABLE_BASELINE',
                        public_protocol=public.observed_configuration.get('public_protocol', {}))
            self._event('hypotheses', 'started', 'Generating possible explanations; action source pending confirmation')
            return super().hypothesize(case_id)

        def _plan(self, case_id):
            self._event('plan', 'started', 'Requesting a structured test ranking; live response not yet confirmed')
            return super()._plan(case_id)

        def run_lammps(self, experiment_id):
            proposal = self._proposal(experiment_id)
            self._console_context = dict(experiment_id=experiment_id, intervention=proposal.intervention.value,
                                         replicate_total=len(proposal.matched_seeds))
            self._console_call = 0
            self._event('simulate', 'started', 'Starting a registered physical comparison', **self._console_context)
            try:
                result = super().run_lammps(experiment_id)
                checks_passed = result.numerical_check.is_valid and all(run.numerical_check.is_valid for run in self.baseline_runs.get(experiment_id, []))
                self._event('simulate', 'completed' if checks_passed else 'failed',
                            'Registered physical comparison finished' if checks_passed else 'Comparison finished with failed simulation checks',
                            **self._console_context, comparison_complete=True, result_id=result.sim_id,
                            numerical_valid=checks_passed, outcome=result.outcome.value)
                return result
            finally:
                self._console_context = None

        def _run(self, specimen, fresh=False):
            context = dict(self._console_context or {})
            if context:
                context.update(role='baseline' if self._console_call % 2 == 0 else 'test_change',
                               replicate_index=self._console_call // 2 + 1)
                self._console_call += 1
            context.update(seed=specimen.protocol.seed, fresh_requested=fresh)
            self._event('simulate', 'started', 'Computing a new simulation' if fresh else 'Resolving a saved or new simulation',
                        engine_requested=engine_capabilities()['engine'], **context)
            result = super()._run(specimen, fresh=fresh)
            evidence = next((e for e in reversed(self.state.audit_log) if e['stage'] == 'simulation' and e.get('result_id') == result.sim_id), {})
            failed = result.outcome.value == 'EXECUTION_FAILED'
            self._event('simulate', 'failed' if failed else 'completed',
                        'Simulation failed its execution checks' if failed else 'Saved simulation loaded' if evidence.get('cached') else 'New simulation finished',
                        **context, cached=evidence.get('cached'), result_id=result.sim_id,
                        outcome=result.outcome.value, engine_used=result.engine_used,
                        protocol_hash=result.protocol_hash, initial_configuration_hash=result.initial_configuration_hash,
                        units=result.units, wall_time_sec=result.wall_time_sec,
                        max_observed_strain=result.max_observed_strain, failure_strain=result.failure_strain,
                        numerical_check=result.numerical_check.model_dump(mode='json'), error_code=result.error_code)
            return result

        def compare_outcomes(self, baseline_id, experiment_id):
            self._event('verify', 'started', 'Checking numerical reliability and measured physical evidence', experiment_id=experiment_id)
            result = super().compare_outcomes(baseline_id, experiment_id)
            self._event('verify', 'completed', 'Independent evidence verification finished', verification=result)
            return result

        def evaluate_hypotheses(self, case_id):
            before = {h.id: h.confidence for h in self.state.hypotheses}
            self._event('revise', 'started', 'Revising explanations using completed evidence; action source pending confirmation')
            result = super().evaluate_hypotheses(case_id)
            self._event('revise', 'completed', 'Explanation update recorded', hypotheses=hypotheses(self.state),
                        belief_changes=[dict(hypothesis_id=h.id, before=before.get(h.id), after=h.confidence,
                                             verifier_status=h.status.value) for h in self.state.hypotheses],
                        ai_execution_mode=self.state.ai_execution_mode.value, receipt=receipt(self.state))
            return result

        def generate_report(self, case_id):
            self._event('conclude', 'started', 'Preparing a conclusion from the verified evidence')
            result = super().generate_report(case_id)
            self._event('conclude', 'completed', 'Scientific conclusion recorded',
                        scientific_status=result.status, summary=result.final_verdict_summary,
                        identified_cause=result.identified_cause.value if result.identified_cause else None)
            return result

    return ObservedInvestigator
