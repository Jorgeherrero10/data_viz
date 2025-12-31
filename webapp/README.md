# Madrid Housing Analysis Dashboard - Web Application

This is a Next.js web application version of the Madrid Housing Analysis Dashboard, designed for deployment on Vercel.

## Features

The dashboard includes three main views:

1. **Strategic Overview** - Rent price trends, district comparisons, youth salary vs rent analysis
2. **Tactical Decisions** - Smart rent control implementation analysis with landlord incentives
3. **Analytical Insights** - Deep-dive financial analysis with budget flow and projections

## Screenshots

### Dashboard 1: Strategic Overview
Rent price trends, district comparisons, and youth salary vs rent analysis.

![Strategic Overview](https://github.com/user-attachments/assets/b5aee3a0-bf74-4ca8-a9ae-db95e361db80)

### Dashboard 2: Tactical Decisions
Smart rent control implementation analysis with landlord incentives.

![Tactical Decisions](https://github.com/user-attachments/assets/1f49badc-0dee-4c71-8fa0-9ebd190e68f5)

### Dashboard 3: Analytical Insights
Deep-dive financial analysis with budget flow and projections.

![Analytical Insights](https://github.com/user-attachments/assets/cc631427-c8ec-47a4-8655-856f86244676)

## Getting Started

### Prerequisites

- Node.js 18.x or higher
- npm 9.x or higher

### Installation

```bash
cd webapp
npm install
```

### Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to see the dashboard.

### Production Build

```bash
npm run build
npm start
```

## Deployment on Vercel

### Option 1: Deploy via Vercel CLI

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. From the `webapp` directory, run:
   ```bash
   vercel
   ```

3. Follow the prompts to link your project and deploy.

### Option 2: Deploy via Vercel Dashboard

1. Push your code to a GitHub repository
2. Go to [vercel.com](https://vercel.com) and sign up/log in
3. Click "New Project"
4. Import your GitHub repository
5. Set the **Root Directory** to `webapp`
6. Click "Deploy"

### Environment Configuration

No environment variables are required for basic functionality. The application uses static data files included in the `public/data` directory.

## Project Structure

```
webapp/
├── app/                    # Next.js App Router pages
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Main dashboard page
├── components/            # React components
│   └── PlotWrapper.tsx    # Dynamic Plotly wrapper
├── lib/                   # Utility functions and data
│   └── data.ts           # Data processing and calculations
├── public/               # Static assets
│   └── data/             # CSV and GeoJSON data files
├── package.json          # Dependencies and scripts
├── tsconfig.json         # TypeScript configuration
├── tailwind.config.js    # Tailwind CSS configuration
├── next.config.js        # Next.js configuration
└── vercel.json           # Vercel deployment configuration
```

## Technologies Used

- **Next.js 14** - React framework with App Router
- **React 18** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS
- **Plotly.js** - Interactive charts and visualizations
- **React-Plotly.js** - React wrapper for Plotly

## Data Sources

- INE (Instituto Nacional de Estadística)
- CIS (Centro de Investigaciones Sociológicas)
- Madrid Data Portal
- El Confidencial (2024)

## License

This project is for educational and demonstration purposes.
