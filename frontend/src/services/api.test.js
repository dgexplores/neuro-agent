import api, { submitDemoAssessment } from './api';

beforeEach(() => sessionStorage.clear());

test('demo requests carry only a sample ID and the current tab token', async () => {
  sessionStorage.setItem('neuroagent_token', 'tab-session');
  let captured;
  api.defaults.adapter = async (config) => {
    captured = config;
    return { data: { case_id: 'owned-result' }, status: 200, statusText: 'OK', headers: {}, config };
  };
  expect(await submitDemoAssessment('fictional-headache')).toEqual({ case_id: 'owned-result' });
  expect(captured.url).toBe('/api/v1/demo/diagnosis');
  expect(JSON.parse(captured.data)).toEqual({ sample_id: 'fictional-headache' });
  expect(captured.headers.Authorization).toBe('Bearer tab-session');
});

test.each([401, 429, 502, 503])('demo failure %s remains a rejected request', async (status) => {
  api.defaults.adapter = async () => { throw { response: { status } }; };
  await expect(submitDemoAssessment('fictional-headache')).rejects.toThrow(
    status === 401 ? /expired/ : status === 429 ? /budget/ : status === 502 ? /invalid response/ : /unavailable/
  );
});
