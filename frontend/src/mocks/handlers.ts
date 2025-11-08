import { rest } from 'msw';

const handlers = [
  rest.post('/api/v1/auth/login', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        access_token: 'mock-token',
        token_type: 'bearer',
        user: {
          id: '1',
          email: 'test@example.com',
          full_name: 'Test User',
          is_active: true,
        },
      })
    );
  }),

  rest.get('/api/v1/auth/me', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        id: '1',
        email: 'test@example.com',
        full_name: 'Test User',
        is_active: true,
      })
    );
  }),

  rest.post('/api/v1/books/search', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        {
          id: '1',
          title: 'Test Book',
          author: 'Test Author',
          year: 2023,
          genre: 'Fiction',
          description: 'A test book description',
        },
      ])
    );
  }),

  rest.post('/api/v1/payments/create-payment-intent', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        client_secret: 'mock_client_secret',
        amount: 999,
        currency: 'usd',
      })
    );
  }),
];

export { handlers };