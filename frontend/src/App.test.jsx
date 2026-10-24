import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from './App';
import { getDemoConfig, startDemoSession } from './services/api';

vi.mock('./services/api', () => ({
  getDemoConfig: vi.fn(), startDemoSession: vi.fn(), submitDemoAssessment: vi.fn(),
  submitDiagnosis: vi.fn(), getCase: vi.fn(),
}));

beforeEach(() => {
  sessionStorage.clear();
  vi.clearAllMocks();
  getDemoConfig.mockResolvedValue({ enabled: false });
});

test('keeps assessment and case routes working with the actual router', () => {
  render(<MemoryRouter><App /></MemoryRouter>);
  fireEvent.click(screen.getByRole('button', { name: 'Look up a saved case' }));
  expect(screen.getByRole('heading', { name: 'Saved cases' })).toBeInTheDocument();
  fireEvent.click(screen.getByRole('tab', { name: 'Home' }));
  fireEvent.click(screen.getByRole('button', { name: 'Try an assessment' }));
  expect(screen.getByText('Educational assessment')).toBeInTheDocument();
});

test('retains session-token save and clear controls', () => {
  render(<MemoryRouter><App /></MemoryRouter>);
  fireEvent.click(screen.getByRole('button', { name: 'Advanced API access' }));
  fireEvent.change(screen.getByLabelText('Bearer token'), { target: { value: ' short-lived-example ' } });
  fireEvent.click(screen.getByRole('button', { name: 'Save token' }));
  expect(sessionStorage.getItem('neuroagent_token')).toBe('short-lived-example');
  fireEvent.click(screen.getByRole('button', { name: 'Clear token' }));
  expect(sessionStorage.getItem('neuroagent_token')).toBeNull();
});

test('starts a scoped synthetic session without asking for credentials', async () => {
  getDemoConfig.mockResolvedValue({ enabled: true, samples: [] });
  startDemoSession.mockResolvedValue({ access_token: 'synthetic-session', expires_in: 900, scope: 'demo' });
  render(<MemoryRouter><App /></MemoryRouter>);
  expect(screen.queryByLabelText('Bearer token')).not.toBeInTheDocument();
  fireEvent.click(await screen.findByRole('button', { name: 'Start synthetic demo' }));
  expect(await screen.findByRole('heading', { name: 'Synthetic demonstration' })).toBeInTheDocument();
  expect(sessionStorage.getItem('neuroagent_token')).toBe('synthetic-session');
  expect(JSON.parse(sessionStorage.getItem('neuroagent_demo_session')).expiresAt).toBeGreaterThan(Date.now());
  fireEvent.click(screen.getByRole('tab', { name: 'Assessment' }));
  expect(screen.getByText(/This session can run fictional examples only/)).toBeInTheDocument();
  expect(screen.queryByLabelText(/Chief complaint/)).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: 'End demo session' }));
  expect(sessionStorage.getItem('neuroagent_token')).toBeNull();
});

test('clears an expired demo session while keeping the advanced connection option', async () => {
  sessionStorage.setItem('neuroagent_token', 'expired-example');
  sessionStorage.setItem('neuroagent_demo_session', JSON.stringify({ expiresAt: Date.now() - 1000 }));
  render(<MemoryRouter><App /></MemoryRouter>);
  expect(await screen.findByText(/Your demo session expired/)).toBeInTheDocument();
  expect(sessionStorage.getItem('neuroagent_token')).toBeNull();
  expect(screen.getByRole('button', { name: 'Advanced API access' })).toBeInTheDocument();
});

test('does not issue sessions when demo access is disabled', async () => {
  render(<MemoryRouter><App /></MemoryRouter>);
  await waitFor(() => expect(getDemoConfig).toHaveBeenCalledOnce());
  expect(screen.queryByRole('button', { name: 'Start synthetic demo' })).not.toBeInTheDocument();
  expect(startDemoSession).not.toHaveBeenCalled();
});

test('offers a home link for unknown routes', () => {
  render(<MemoryRouter initialEntries={['/does-not-exist']}><App /></MemoryRouter>);
  expect(screen.getByRole('heading', { name: 'Page not found' })).toBeInTheDocument();
  fireEvent.click(screen.getByRole('link', { name: 'Go home' }));
  expect(screen.getByRole('button', { name: 'Try an assessment' })).toBeInTheDocument();
});

test('redirects the cases alias to the saved-case workflow', () => {
  render(<MemoryRouter initialEntries={['/cases']}><App /></MemoryRouter>);
  expect(screen.getByRole('heading', { name: 'Saved cases' })).toBeInTheDocument();
});
