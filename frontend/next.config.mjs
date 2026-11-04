/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    // Tout /api/* est proxye vers le backend Django (pas de CORS a gerer)
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
    ];
  },
};

export default nextConfig;
