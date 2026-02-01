# PrepIt Frontend

A modern data preprocessing and analysis platform built with Next.js, TypeScript, and Tailwind CSS.

## Tech Stack

- **Framework**: Next.js 16.0.10
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4.1.9
- **UI Components**: Radix UI + shadcn/ui
- **Authentication**: Firebase Auth
- **State Management**: React Context
- **Forms**: React Hook Form + Zod
- **Charts**: Recharts
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 18.17.0 or higher
- pnpm (recommended) or npm
- Firebase project credentials

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd Frontend
```

2. Install dependencies:
```bash
pnpm install
# or
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env.local
```

4. Update `.env.local` with your credentials:
   - Backend API URL
   - Firebase configuration

### Development

Run the development server:

```bash
pnpm dev
# or
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

Create a production build:

```bash
pnpm build
# or
npm run build
```

### Start Production Server

```bash
pnpm start
# or
npm start
```

## Project Structure

```
Frontend/
├── app/                    # Next.js app directory
│   ├── dashboard/         # Dashboard pages
│   ├── history/           # Processing history
│   ├── insights/          # Data insights
│   ├── login/             # Login page
│   ├── signup/            # Signup page
│   ├── upload/            # File upload
│   └── layout.tsx         # Root layout
├── components/            # React components
│   ├── dashboard/         # Dashboard-specific components
│   ├── layout/            # Layout components
│   └── ui/                # shadcn/ui components
├── context/               # React context providers
├── hooks/                 # Custom React hooks
├── lib/                   # Utility functions and configs
│   ├── api-client.ts      # API client
│   ├── api-config.ts      # API configuration
│   ├── firebase.ts        # Firebase setup
│   └── utils.ts           # Helper functions
└── public/                # Static assets
```

## Features

- 🔐 **Authentication**
  - Email/Password authentication
  - Google Sign-In
  - Protected routes
  - Persistent sessions

- 📊 **Dashboard**
  - File upload with drag-and-drop
  - Real-time processing stats
  - Data preview
  - Analytics charts

- 📁 **History**
  - Processing history tracking
  - Downloadable results
  - Detailed analytics

- 🎨 **UI/UX**
  - Dark/Light theme
  - Responsive design
  - Modern glassmorphism effects
  - Smooth animations

## Environment Variables

See [.env.example](./.env.example) for all required environment variables.

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions for Vercel.

### Quick Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=<your-repo-url>&env=NEXT_PUBLIC_API_URL,NEXT_PUBLIC_FIREBASE_API_KEY,NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,NEXT_PUBLIC_FIREBASE_PROJECT_ID,NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,NEXT_PUBLIC_FIREBASE_APP_ID)

## Scripts

| Script | Description |
|--------|-------------|
| `pnpm dev` | Start development server |
| `pnpm build` | Create production build |
| `pnpm start` | Start production server |
| `pnpm lint` | Run ESLint |

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Create an issue on GitHub
- Check [DEPLOYMENT.md](./DEPLOYMENT.md) for deployment help
- Review Firebase and Next.js documentation

---

Built with ❤️ using Next.js and TypeScript
