import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from './App';

beforeEach(() => sessionStorage.clear());

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
  fireEvent.change(screen.getByLabelText('Bearer token'), { target: { value: ' short-lived-example ' } });
  fireEvent.click(screen.getByRole('button', { name: 'Save token' }));
  expect(sessionStorage.getItem('neuroagent_token')).toBe('short-lived-example');
  fireEvent.click(screen.getByRole('button', { name: 'Clear token' }));
  expect(sessionStorage.getItem('neuroagent_token')).toBeNull();
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
