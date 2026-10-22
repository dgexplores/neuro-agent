import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import HomePage from './HomePage';

const { mockNavigate } = vi.hoisted(() => ({ mockNavigate: vi.fn() }));
vi.mock('react-router-dom', () => ({ useNavigate: () => mockNavigate }));
beforeEach(() => vi.clearAllMocks());

test('identifies the prototype and preserves original authorship', () => {
  render(<HomePage />);
  expect(screen.getByText(/has not been clinically validated/)).toBeTruthy();
  expect(screen.getByRole('link', { name: 'dgexplores' }).getAttribute('href')).toBe('https://github.com/dgexplores');
  expect(screen.getByRole('link', { name: 'upstream NeuroAgent project' }).getAttribute('href')).toBe('https://github.com/thc1006/neuro-agent');
});

test('retains the assessment and saved-case navigation paths', () => {
  render(<HomePage />);
  fireEvent.click(screen.getByRole('button', { name: 'Try an assessment' }));
  fireEvent.click(screen.getByRole('button', { name: 'Look up a saved case' }));
  expect(mockNavigate.mock.calls).toEqual([['/diagnosis'], ['/history']]);
});
