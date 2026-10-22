import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import DiagnosisPage from './DiagnosisPage';
import { submitDiagnosis } from '../services/api';
vi.mock('../services/api', () => ({ submitDiagnosis: vi.fn() }));
beforeEach(() => vi.clearAllMocks());
const fillRequired = () => {
  fireEvent.change(screen.getByLabelText(/Age/), { target: { value: '32' } });
  fireEvent.mouseDown(screen.getByRole('combobox', { name: /Gender/ }));
  fireEvent.click(screen.getByRole('option', { name: 'Female' }));
  fireEvent.change(screen.getByLabelText(/Chief complaint/), { target: { value: 'Synthetic headache' } });
  fireEvent.change(screen.getByLabelText(/Symptoms/), { target: { value: 'headache, nausea' } });
};
test('submits blank optional vital signs as an empty object, not invalid null fields', async () => {
  submitDiagnosis.mockRejectedValue(new Error('Synthetic provider unavailable'));
  render(<DiagnosisPage />); fillRequired();
  fireEvent.click(screen.getByRole('button', { name: 'Run assessment' }));
  await waitFor(() => expect(submitDiagnosis).toHaveBeenCalledOnce());
  expect(submitDiagnosis.mock.calls[0][0].vital_signs).toEqual({});
  expect(submitDiagnosis.mock.calls[0][0].patient_info.age).toBe(32);
  expect(await screen.findByText('Synthetic provider unavailable')).toBeInTheDocument();
});
test('blocks a malformed blood pressure before calling the API', async () => {
  render(<DiagnosisPage />); fillRequired();
  fireEvent.change(screen.getByLabelText(/Blood pressure/), { target: { value: 'wrong' } });
  fireEvent.click(screen.getByRole('button', { name: 'Run assessment' }));
  expect(await screen.findByText(/Enter blood pressure as/)).toBeInTheDocument();
  expect(submitDiagnosis).not.toHaveBeenCalled();
});
