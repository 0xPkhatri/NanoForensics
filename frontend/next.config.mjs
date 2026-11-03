const config = { poweredByHeader: false, async rewrites() {
  const backend = process.env.NANO_BACKEND_URL || 'http://127.0.0.1:8000';
  return [
    {source:'/api/:path*',destination: `${backend}/api/:path*`},
    {source:'/study-evidence/:path*',destination: `${backend}/study-evidence/:path*`},
  ];
} };
export default config;
