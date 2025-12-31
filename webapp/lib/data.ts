// Data types for the dashboard
export interface PriceData {
  Date: string;
  District: string;
  COD_DIS: string;
  Rent_Price: number | null;
}

export interface YouthSalaryData {
  Year: number;
  Average_Youth_Salary: number;
  Average_Monthly_Rent: number;
}

export interface GeoJSONFeature {
  type: string;
  properties: {
    NOMBRE: string;
    COD_DIS: string;
    [key: string]: any;
  };
  geometry: {
    type: string;
    coordinates: number[][][];
  };
}

export interface GeoJSONData {
  type: string;
  features: GeoJSONFeature[];
}

// Radar chart data
export const radarData = {
  years: [2014, 2024],
  categories: ['Access to Housing', 'Unemployment', 'Political Issues', 'Job Quality', 'Immigration', 'Economic Crisis'],
  values: {
    2014: [5, 8, 6, 7, 4, 7],
    2024: [9, 7, 6, 7, 5, 6]
  }
};

// Dashboard 2 data
export const dashboardTwoData = {
  districts: ["Salamanca", "Centro", "Chamberí", "Chamartín", "Arganzuela", "Tetuán", "Retiro", "Moncloa-Aravaca", "Fuencarral-El Pardo", "Usera"],
  beforeControl: [25, 24, 23, 22, 20, 18, 21, 19, 17, 16],
  afterControl: [21, 20, 20, 19, 18, 16, 18, 17, 15, 14],
  incentiveLevels: ['No Incentives', 'Partial Incentives', 'Full Incentives'],
  participationRates: [10, 40, 70],
  rentIncrease: [5.0, 3.0, 1.5],
  netBenefit: [0, 3000, 5873],
  tenantCategories: ["Low-Income Renters", "Middle-Income Renters", "Young Professionals"],
  beforeBurden: [51.7, 35.4, 41.2],
  afterBurden: [39.4, 25.9, 30.9],
  districtSubset: ["Salamanca", "Centro", "Chamberí", "Retiro", "Arganzuela"],
  youthBefore: [42.5, 39.3, 39.9, 44.4, 41.2],
  youthAfter: [29.7, 29.0, 30.3, 31.6, 30.0],
  lowIncomeBefore: [54.9, 52.8, 54.6, 52.0, 46.0],
  lowIncomeAfter: [44.9, 41.4, 41.8, 40.2, 33.6]
};

// Dashboard 3 data
export const dashboardThreeData = {
  sankeyData: {
    nodeLabels: ["Total Housing Budget", "Tax Incentives", "Remaining Budget", "Affordable Housing Programs", "Rental Assistance", "Other Housing Initiatives"],
    nodeColors: ["#3498db", "#e74c3c", "#2980b9", "#27ae60", "#8e44ad", "#f39c12"],
    linkSources: [0, 0, 2, 2, 2],
    linkTargets: [1, 2, 3, 4, 5],
    linkValues: [27.8, 72.2, 24, 28.2, 20],
    linkColors: ["rgba(231, 76, 60, 0.4)", "rgba(41, 128, 185, 0.4)", "rgba(39, 174, 96, 0.4)", "rgba(142, 68, 173, 0.4)", "rgba(243, 156, 18, 0.4)"]
  },
  years: Array.from({length: 10}, (_, i) => 2025 + i),
  currentPropertyTax: 500,
  socialImpact: 25.2,
  districts: ["Salamanca", "Centro", "Chamberí", "Chamartín", "Arganzuela", "Tetuán", "Retiro", "Moncloa-Aravaca", "Fuencarral-El Pardo", "Usera"],
  affordabilityImprovement: [30.1, 26.5, 24.3, 23.7, 20.5, 19.8, 22.1, 21.5, 18.7, 17.2],
  incentiveCost: [235, 220, 210, 190, 160, 150, 180, 175, 140, 125],
  implementationComplexity: [4, 4, 3, 3, 2, 2, 3, 3, 2, 1]
};

// Calculate CAGR
export function calculateCAGR(prices: PriceData[], district: string): number | null {
  const filtered = district === 'All' 
    ? prices 
    : prices.filter(p => p.District === district);
  
  const validPrices = filtered
    .filter(p => p.Rent_Price !== null && p.Rent_Price > 0 && new Date(p.Date) >= new Date('2012-01-01'))
    .sort((a, b) => new Date(a.Date).getTime() - new Date(b.Date).getTime());
  
  if (validPrices.length < 2) return null;
  
  const initialPrice = validPrices[0].Rent_Price!;
  const finalPrice = validPrices[validPrices.length - 1].Rent_Price!;
  const years = (new Date(validPrices[validPrices.length - 1].Date).getTime() - new Date(validPrices[0].Date).getTime()) / (365.25 * 24 * 60 * 60 * 1000);
  
  if (years <= 0) return null;
  
  return ((finalPrice / initialPrice) ** (1 / years) - 1) * 100;
}

// Calculate max price
export function calculateMaxPrice(prices: PriceData[], district: string): number | null {
  const filtered = district === 'All' 
    ? prices 
    : prices.filter(p => p.District === district);
  
  const validPrices = filtered.filter(p => p.Rent_Price !== null && p.Rent_Price > 0);
  if (validPrices.length === 0) return null;
  
  return Math.max(...validPrices.map(p => p.Rent_Price!));
}

// Calculate ranking
export function calculateRanking(prices: PriceData[], district: string): number | null {
  if (district === 'All') return null;
  
  const districtAvgs: {[key: string]: number} = {};
  prices.forEach(p => {
    if (p.Rent_Price !== null && p.Rent_Price > 0) {
      if (!districtAvgs[p.District]) {
        districtAvgs[p.District] = 0;
      }
      districtAvgs[p.District] += p.Rent_Price;
    }
  });
  
  const districtCounts: {[key: string]: number} = {};
  prices.forEach(p => {
    if (p.Rent_Price !== null && p.Rent_Price > 0) {
      districtCounts[p.District] = (districtCounts[p.District] || 0) + 1;
    }
  });
  
  Object.keys(districtAvgs).forEach(d => {
    districtAvgs[d] = districtAvgs[d] / districtCounts[d];
  });
  
  const sorted = Object.entries(districtAvgs).sort((a, b) => b[1] - a[1]);
  const rank = sorted.findIndex(([d]) => d === district) + 1;
  
  return rank > 0 ? rank : null;
}

// Calculate average price
export function calculateAvgPrice(prices: PriceData[], district: string): number | null {
  const filtered = district === 'All' 
    ? prices 
    : prices.filter(p => p.District === district);
  
  const validPrices = filtered.filter(p => p.Rent_Price !== null && p.Rent_Price > 0);
  if (validPrices.length === 0) return null;
  
  const sum = validPrices.reduce((acc, p) => acc + p.Rent_Price!, 0);
  return sum / validPrices.length;
}

// Calculate required income (based on 40% rent expenditure)
export function calculateRequiredIncome(avgPrice: number | null, surface: number = 100): number | null {
  if (avgPrice === null) return null;
  return (avgPrice * surface) / 0.4;
}

// Get color for map based on value
export function getMapColor(value: number, minVal: number, maxVal: number): string {
  const norm = maxVal > minVal ? (value - minVal) / (maxVal - minVal) : 0;
  const redLevel = Math.round(norm * 255);
  return `#${redLevel.toString(16).padStart(2, '0')}0000`;
}

// Process prices for line chart
export function processLineChartData(prices: PriceData[], selectedDistricts: string[]) {
  const validPrices = prices.filter(p => p.Rent_Price !== null && p.Rent_Price > 0);
  
  // Group by date and district
  const grouped: {[key: string]: {[key: string]: number[]}} = {};
  validPrices.forEach(p => {
    if (!grouped[p.Date]) grouped[p.Date] = {};
    if (!grouped[p.Date][p.District]) grouped[p.Date][p.District] = [];
    grouped[p.Date][p.District].push(p.Rent_Price!);
  });
  
  // Calculate averages
  const result: {Date: string; District: string; Rent_Price: number}[] = [];
  const overallByDate: {[key: string]: number[]} = {};
  
  Object.entries(grouped).forEach(([date, districts]) => {
    Object.entries(districts).forEach(([district, vals]) => {
      const avg = vals.reduce((a, b) => a + b, 0) / vals.length;
      result.push({ Date: date, District: district, Rent_Price: avg });
      
      if (!overallByDate[date]) overallByDate[date] = [];
      overallByDate[date].push(avg);
    });
  });
  
  // Calculate overall mean
  const overall = Object.entries(overallByDate).map(([date, vals]) => ({
    Date: date,
    Rent_Price: vals.reduce((a, b) => a + b, 0) / vals.length
  })).sort((a, b) => new Date(a.Date).getTime() - new Date(b.Date).getTime());
  
  // Filter by selected districts if any
  const filtered = selectedDistricts.length > 0 
    ? result.filter(p => selectedDistricts.includes(p.District))
    : result;
  
  return { data: filtered.sort((a, b) => new Date(a.Date).getTime() - new Date(b.Date).getTime()), overall };
}

// Get district averages
export function getDistrictAverages(prices: PriceData[]): {[key: string]: number} {
  const sums: {[key: string]: number} = {};
  const counts: {[key: string]: number} = {};
  
  prices.forEach(p => {
    if (p.Rent_Price !== null && p.Rent_Price > 0) {
      sums[p.District] = (sums[p.District] || 0) + p.Rent_Price;
      counts[p.District] = (counts[p.District] || 0) + 1;
    }
  });
  
  const avgs: {[key: string]: number} = {};
  Object.keys(sums).forEach(d => {
    avgs[d] = sums[d] / counts[d];
  });
  
  return avgs;
}
