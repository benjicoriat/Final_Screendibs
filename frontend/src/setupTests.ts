/* eslint-disable no-undef */
import '@testing-library/jest-dom';
import { server } from './mocks/server';

beforeAll(() => {
  // Enable the mocking in tests.
  server.listen();
});

afterEach(() => {
  // Reset any runtime handlers tests may use.
  server.resetHandlers();
});

afterAll(() => {
  // Clean up after all tests are done.
  server.close();
});
/* eslint-enable no-undef */