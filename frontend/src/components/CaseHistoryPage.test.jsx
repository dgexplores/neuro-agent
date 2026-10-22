import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import CaseHistoryPage from './CaseHistoryPage';
import { getCase } from '../services/api';

vi.mock('../services/api', () => ({ getCase: vi.fn() }));

beforeEach(() => vi.clearAllMocks());

const submitCase = (id) => {
  fireEvent.change(screen.getByLabelText(/case id/i), { target: { value: id } });
  fireEvent.click(screen.getByRole('button', { name: 'Find case' }));
};

test('starts empty without fabricated cases or an unsupported list request', () => {
  render(<CaseHistoryPage />);
  expect(screen.getByText(/No case loaded/)).toBeTruthy();
  expect(getCase).not.toHaveBeenCalled();
  expect(screen.getByRole('button', { name: 'Find case' }).disabled).toBe(true);
});

test('retrieves the trimmed ID and displays the stored assessment', async () => {
  getCase.mockResolvedValue({
    case_id: 'saved-case', diagnosis: [{ condition: 'Stored example', reasoning: 'Stored reasoning' }],
    recommendations: ['Stored recommendation'], risk_factors: ['Stored factor'], next_steps: ['Stored follow-up']
  });
  render(<CaseHistoryPage />);
  submitCase('  saved-case  ');
  expect(await screen.findByText('Stored example')).toBeTruthy();
  expect(getCase).toHaveBeenCalledWith('saved-case');
  expect(screen.getByText('Stored recommendation')).toBeTruthy();
  expect(screen.getByText('Stored follow-up')).toBeTruthy();
});

test.each([
  [404, /Case not found/],
  [401, /Sign in with a valid access token/],
  [503, /Unable to retrieve this case/]
])('handles API status %i without creating a substitute case', async (status, message) => {
  getCase.mockRejectedValue({ response: { status } });
  render(<CaseHistoryPage />);
  submitCase('missing');
  expect(await screen.findByText(message)).toBeTruthy();
  expect(screen.queryByLabelText('Saved case result')).toBeNull();
});

test('clears a previously loaded result when the next lookup fails', async () => {
  getCase.mockResolvedValueOnce({ case_id: 'first', diagnosis: [{ condition: 'First result' }] })
    .mockRejectedValueOnce({ response: { status: 404 } });
  render(<CaseHistoryPage />);
  submitCase('first');
  await screen.findByText('First result');
  await waitFor(() => expect(screen.getByRole('button', { name: 'Find case' }).disabled).toBe(false));
  submitCase('second');
  await screen.findByText(/Case not found/);
  expect(screen.queryByText('First result')).toBeNull();
});
