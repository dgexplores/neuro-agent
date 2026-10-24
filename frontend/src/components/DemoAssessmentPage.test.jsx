import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import DemoAssessmentPage from './DemoAssessmentPage';
import { submitDemoAssessment } from '../services/api';

vi.mock('../services/api', () => ({ submitDemoAssessment: vi.fn() }));
const config = { enabled: true, samples: [{ id: 'fictional-headache', name: 'Fictional example',
  summary: 'An invented example.', request: { patient_info: { age: 32, gender: 'female' },
    symptoms: [{ name: 'headache' }] } }] };
beforeEach(() => vi.clearAllMocks());

test('submits only the synthetic sample ID and displays the returned case', async () => {
  submitDemoAssessment.mockResolvedValue({ case_id: 'owned-case', confidence: .4,
    diagnosis: [{ condition: 'Synthetic model response', confidence: .4 }],
    recommendations: [], risk_factors: [], next_steps: [] });
  render(<DemoAssessmentPage config={config} active />);
  fireEvent.click(screen.getByRole('button', { name: 'Run fictional example' }));
  await waitFor(() => expect(submitDemoAssessment).toHaveBeenCalledWith('fictional-headache'));
  expect(await screen.findByText('Case ID: owned-case')).toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'Run fictional example' })).toBeDisabled();
});

test('surfaces a provider failure and never substitutes a successful result or automatic retry', async () => {
  submitDemoAssessment.mockRejectedValue(new Error('The model is unavailable. This attempt has been used.'));
  render(<DemoAssessmentPage config={config} active />);
  fireEvent.click(screen.getByRole('button', { name: 'Run fictional example' }));
  expect(await screen.findByText(/The model is unavailable/)).toBeInTheDocument();
  expect(screen.queryByText('Assessment results')).not.toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'Run fictional example' })).toBeDisabled();
  expect(submitDemoAssessment).toHaveBeenCalledOnce();
});

test('requires an active session and offers no free-text input', () => {
  render(<DemoAssessmentPage config={config} active={false} />);
  expect(screen.getByRole('button', { name: 'Run fictional example' })).toBeDisabled();
  expect(screen.queryByRole('textbox')).not.toBeInTheDocument();
  expect(submitDemoAssessment).not.toHaveBeenCalled();
});
