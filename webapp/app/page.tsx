'use client';

import { useState, useEffect } from 'react';
import Plot from '@/components/PlotWrapper';
import {
  PriceData,
  YouthSalaryData,
  GeoJSONData,
  radarData,
  dashboardTwoData,
  dashboardThreeData,
  calculateCAGR,
  calculateMaxPrice,
  calculateRanking,
  calculateAvgPrice,
  calculateRequiredIncome,
  processLineChartData,
  getDistrictAverages,
  getMapColor
} from '@/lib/data';

type DashboardPage = 'dashboard1' | 'dashboard2' | 'dashboard3';

export default function Home() {
  const [currentPage, setCurrentPage] = useState<DashboardPage>('dashboard1');
  const [priceData, setPriceData] = useState<PriceData[]>([]);
  const [youthSalaryData, setYouthSalaryData] = useState<YouthSalaryData[]>([]);
  const [geoJSONData, setGeoJSONData] = useState<GeoJSONData | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Dashboard 1 filters
  const [selectedDistricts, setSelectedDistricts] = useState<string[]>([]);
  const [kpiDistrict, setKpiDistrict] = useState('All');
  const [requiredIncomeDistrict, setRequiredIncomeDistrict] = useState('All');
  
  // Dashboard 2 filters
  const [d2SelectedDistricts, setD2SelectedDistricts] = useState<string[]>([]);
  const [d2IncentiveLevel, setD2IncentiveLevel] = useState('Full Incentives');
  const [d2Timeline, setD2Timeline] = useState(4);
  const [d2TenantCategories, setD2TenantCategories] = useState<string[]>(['Low-Income Renters', 'Young Professionals']);
  const [d2Tab, setD2Tab] = useState('Implementation Strategy');
  
  // Dashboard 3 filters
  const [d3IncentiveBudget, setD3IncentiveBudget] = useState(27.8);
  const [d3TaxSavings, setD3TaxSavings] = useState(7313);
  const [d3GrowthWithout, setD3GrowthWithout] = useState(2.0);
  const [d3GrowthWith, setD3GrowthWith] = useState(3.0);
  const [d3SelectedDistricts, setD3SelectedDistricts] = useState<string[]>([]);
  const [d3AnalysisView, setD3AnalysisView] = useState('Quadrant Analysis');
  const [d3ChartType, setD3ChartType] = useState('Long-term Projection');

  // Load data
  useEffect(() => {
    Promise.all([
      fetch('/data/prices.csv').then(r => r.text()),
      fetch('/data/Youth_Salary_vs_Rent_Prices.csv').then(r => r.text()),
      fetch('/data/DistritosMadrid.geojson').then(r => r.json())
    ]).then(([pricesText, youthText, geoJSON]) => {
      // Parse prices CSV
      const pricesLines = pricesText.split('\n').filter(l => l.trim());
      const pricesHeaders = pricesLines[0].split(',');
      const prices: PriceData[] = pricesLines.slice(1).map(line => {
        const parts = line.split(',');
        return {
          Date: parts[0],
          District: parts[1],
          COD_DIS: parts[2],
          Rent_Price: parts[3] ? parseFloat(parts[3]) : null
        };
      }).filter(p => p.Date && p.District);
      setPriceData(prices);
      
      // Parse youth salary CSV
      const youthLines = youthText.split('\n').filter(l => l.trim());
      const youth: YouthSalaryData[] = youthLines.slice(1).map(line => {
        const parts = line.split(',');
        return {
          Year: parseInt(parts[0]),
          Average_Youth_Salary: parseFloat(parts[1]),
          Average_Monthly_Rent: parseFloat(parts[2])
        };
      }).filter(y => !isNaN(y.Year));
      setYouthSalaryData(youth);
      
      setGeoJSONData(geoJSON);
      setLoading(false);
    }).catch(err => {
      console.error('Error loading data:', err);
      setLoading(false);
    });
  }, []);

  const districts = [...new Set(priceData.map(p => p.District))].filter(Boolean).sort();
  const districtAvgs = getDistrictAverages(priceData);
  const minRent = Math.min(...Object.values(districtAvgs)) || 0;
  const maxRent = Math.max(...Object.values(districtAvgs)) || 1;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="loading">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  const renderDashboard1 = () => {
    const { data: lineData, overall } = processLineChartData(priceData, selectedDistricts);
    const cagr = calculateCAGR(priceData, kpiDistrict);
    const maxPrice = calculateMaxPrice(priceData, kpiDistrict);
    const ranking = calculateRanking(priceData, kpiDistrict);
    const avgPrice = calculateAvgPrice(priceData, kpiDistrict);
    const reqIncomeAvgPrice = calculateAvgPrice(priceData, requiredIncomeDistrict);
    const requiredIncome = calculateRequiredIncome(reqIncomeAvgPrice);
    
    // Group line data by district for plotting
    const districtGroups: {[key: string]: {x: string[], y: number[]}} = {};
    lineData.forEach(d => {
      if (!districtGroups[d.District]) {
        districtGroups[d.District] = { x: [], y: [] };
      }
      districtGroups[d.District].x.push(d.Date);
      districtGroups[d.District].y.push(d.Rent_Price);
    });

    return (
      <>
        <div className="title-bar">
          Strategic Overview: <b>&nbsp;Rent Prices in Madrid represent a serious problem for the youth population.</b>
        </div>
        
        <div className="grid grid-cols-12 gap-4">
          {/* Sidebar */}
          <div className="col-span-3">
            <div className="sidebar">
              <h3>Filters</h3>
              
              <div className="filter-group">
                <label className="filter-label">Select Districts (Map/Line)</label>
                <select 
                  multiple 
                  className="filter-select" 
                  style={{height: '120px'}}
                  value={selectedDistricts}
                  onChange={(e) => setSelectedDistricts(Array.from(e.target.selectedOptions, o => o.value))}
                >
                  {districts.map(d => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>
              
              <hr className="my-4 border-gray-200" />
              
              <h4 className="text-sm font-medium mb-2">KPI Filter</h4>
              <div className="filter-group">
                <label className="filter-label">Select District for KPIs</label>
                <select 
                  className="filter-select"
                  value={kpiDistrict}
                  onChange={(e) => setKpiDistrict(e.target.value)}
                >
                  <option value="All">All</option>
                  {districts.map(d => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
          
          {/* Main content */}
          <div className="col-span-9">
            <div className="grid grid-cols-2 gap-4">
              {/* Left column */}
              <div>
                {/* Line Chart */}
                <div className="chart-container">
                  <Plot
                    data={[
                      ...Object.entries(districtGroups).map(([district, data]) => ({
                        x: data.x,
                        y: data.y,
                        type: 'scatter',
                        mode: 'lines',
                        name: district,
                        opacity: selectedDistricts.length > 0 ? 1 : 0.5
                      })),
                      {
                        x: overall.map(o => o.Date),
                        y: overall.map(o => o.Rent_Price),
                        type: 'scatter',
                        mode: 'lines',
                        name: 'Overall Mean',
                        line: { dash: 'dash', color: 'black' },
                        opacity: selectedDistricts.length > 0 ? 0.2 : 1
                      }
                    ]}
                    layout={{
                      title: selectedDistricts.length > 0 
                        ? `Average Rent Price by Date - ${selectedDistricts.join(', ')}`
                        : 'Average Rent Price by Date (All Districts)',
                      yaxis: { title: 'Rent Price (€ per M²)', range: [7, 26] },
                      xaxis: { range: ['2008-08-01', '2025-01-01'] },
                      height: 250,
                      margin: { l: 50, r: 20, t: 40, b: 30 },
                      legend: { font: { size: 10 } },
                      showlegend: true
                    }}
                    config={{ displayModeBar: false }}
                    style={{ width: '100%' }}
                  />
                </div>
                
                {/* Map placeholder - simplified visualization */}
                <div className="chart-container">
                  <h4 className="text-sm font-medium mb-2 text-center">Madrid Districts - Rent Price Heat Map</h4>
                  <div className="grid grid-cols-3 gap-2 p-2">
                    {Object.entries(districtAvgs).slice(0, 12).map(([district, avg]) => (
                      <div 
                        key={district}
                        className="p-2 rounded text-xs text-center cursor-pointer transition-all hover:scale-105"
                        style={{ 
                          backgroundColor: getMapColor(avg, minRent, maxRent),
                          color: 'white'
                        }}
                        onClick={() => {
                          if (selectedDistricts.includes(district)) {
                            setSelectedDistricts(selectedDistricts.filter(d => d !== district));
                          } else {
                            setSelectedDistricts([...selectedDistricts, district]);
                          }
                        }}
                      >
                        <div className="font-medium truncate">{district}</div>
                        <div>€{avg.toFixed(1)}/m²</div>
                      </div>
                    ))}
                  </div>
                  <div className="flex justify-center items-center mt-2 text-xs">
                    <span>Low</span>
                    <div className="w-32 h-3 mx-2" style={{background: 'linear-gradient(to right, #000000, #ff0000)'}}></div>
                    <span>High</span>
                  </div>
                </div>
                
                {/* KPI Metrics */}
                <div className="grid grid-cols-4 gap-2 mt-2">
                  <div className="metric-card text-center">
                    <div className="metric-label">CAGR</div>
                    <div className="metric-value text-lg">{cagr !== null ? `${cagr.toFixed(1)}%` : 'N/A'}</div>
                    <div className="text-xs text-gray-500">Annual growth rate</div>
                  </div>
                  <div className="metric-card text-center">
                    <div className="metric-label">Max Rental</div>
                    <div className="metric-value text-lg">{maxPrice !== null ? `€${maxPrice.toFixed(1)}` : 'N/A'}</div>
                    <div className="text-xs text-gray-500">Max Rent (€/m²)</div>
                  </div>
                  <div className="metric-card text-center">
                    <div className="metric-label">Ranking</div>
                    <div className="metric-value text-lg">{ranking !== null ? `#${ranking}` : 'N/A'}</div>
                    <div className="text-xs text-gray-500">By Avg Rent</div>
                  </div>
                  <div className="metric-card text-center">
                    <div className="metric-label">Avg Rent</div>
                    <div className="metric-value text-lg">{avgPrice !== null ? `€${avgPrice.toFixed(1)}` : 'N/A'}</div>
                    <div className="text-xs text-gray-500">Average (€/m²)</div>
                  </div>
                </div>
              </div>
              
              {/* Right column */}
              <div>
                {/* Youth Salary vs Rent Chart */}
                <div className="chart-container">
                  <Plot
                    data={[
                      {
                        x: youthSalaryData.map(d => d.Year),
                        y: youthSalaryData.map(d => d.Average_Youth_Salary),
                        type: 'bar',
                        name: 'Avg Youth Salary',
                        marker: { color: 'lightgray' }
                      },
                      {
                        x: youthSalaryData.map(d => d.Year),
                        y: youthSalaryData.map(d => d.Average_Monthly_Rent),
                        type: 'bar',
                        name: 'Avg Monthly Rent',
                        marker: { color: '#dcef6e' }
                      },
                      {
                        x: youthSalaryData.map(d => d.Year),
                        y: youthSalaryData.map(d => d.Average_Youth_Salary),
                        type: 'scatter',
                        mode: 'lines+markers',
                        name: 'Salary Trend',
                        line: { color: 'darkgray' }
                      },
                      {
                        x: youthSalaryData.map(d => d.Year),
                        y: youthSalaryData.map(d => d.Average_Monthly_Rent),
                        type: 'scatter',
                        mode: 'lines+markers',
                        name: 'Rent Trend',
                        line: { color: '#b0c74a' }
                      }
                    ]}
                    layout={{
                      title: 'Average Youth Salary vs Average Monthly Rent Prices',
                      barmode: 'group',
                      xaxis: { title: 'Year', tickangle: -45 },
                      yaxis: { title: 'Amount in €', range: [600, 1200] },
                      height: 250,
                      margin: { l: 50, r: 20, t: 40, b: 50 },
                      legend: { font: { size: 10 } }
                    }}
                    config={{ displayModeBar: false }}
                    style={{ width: '100%' }}
                  />
                </div>
                
                <div className="grid grid-cols-3 gap-2">
                  {/* Required Income */}
                  <div className="chart-container">
                    <div className="filter-group mb-2">
                      <label className="filter-label">District for Req. Income</label>
                      <select 
                        className="filter-select text-sm"
                        value={requiredIncomeDistrict}
                        onChange={(e) => setRequiredIncomeDistrict(e.target.value)}
                      >
                        <option value="All">All</option>
                        {districts.map(d => (
                          <option key={d} value={d}>{d}</option>
                        ))}
                      </select>
                    </div>
                    <div className="text-center">
                      <div className="text-xs text-gray-500">Req. Income (100m²)</div>
                      <div className="text-xl font-bold">
                        {requiredIncome !== null ? `€${requiredIncome.toLocaleString(undefined, {maximumFractionDigits: 0})}` : 'N/A'}
                      </div>
                      <div className="text-xs text-gray-400">Net income (40% rent)</div>
                    </div>
                  </div>
                  
                  {/* Madrid vs Europe */}
                  <div className="chart-container col-span-2">
                    <Plot
                      data={[{
                        y: ['Europe', 'Madrid'],
                        x: [40, 63],
                        type: 'bar',
                        orientation: 'h',
                        text: ['40%', '63%'],
                        textposition: 'outside',
                        marker: { color: ['#b0c74a', '#dcef6e'] }
                      }]}
                      layout={{
                        title: 'Rent Burden: Madrid vs Europe',
                        xaxis: { range: [0, 100], title: 'Percentage' },
                        height: 150,
                        margin: { l: 60, r: 40, t: 40, b: 30 }
                      }}
                      config={{ displayModeBar: false }}
                      style={{ width: '100%' }}
                    />
                  </div>
                </div>
                
                {/* Radar Chart */}
                <div className="chart-container mt-2">
                  <Plot
                    data={radarData.years.map(year => ({
                      type: 'scatterpolar',
                      r: [...radarData.values[year as 2014 | 2024], radarData.values[year as 2014 | 2024][0]],
                      theta: [...radarData.categories, radarData.categories[0]],
                      fill: 'toself',
                      name: year.toString()
                    }))}
                    layout={{
                      title: 'Concerns Comparison (2014 vs 2024)',
                      polar: { radialaxis: { visible: true, range: [0, 10] } },
                      height: 250,
                      margin: { l: 40, r: 40, t: 40, b: 40 },
                      legend: { font: { size: 10 } }
                    }}
                    config={{ displayModeBar: false }}
                    style={{ width: '100%' }}
                  />
                </div>
              </div>
            </div>
            
            <div className="footer">
              Data Sources: INE, CIS, Madrid Data Portal | District KPI: {kpiDistrict} | Map/Line Selection: {selectedDistricts.length || 'All'}
            </div>
          </div>
        </div>
      </>
    );
  };

  const renderDashboard2 = () => {
    const { districts, beforeControl, afterControl, incentiveLevels, participationRates, rentIncrease, netBenefit, tenantCategories, beforeBurden, afterBurden, districtSubset, youthBefore, youthAfter, lowIncomeBefore, lowIncomeAfter } = dashboardTwoData;
    
    const incentiveIndex = incentiveLevels.indexOf(d2IncentiveLevel);
    const selectedParticipation = participationRates[incentiveIndex];
    const selectedRentIncrease = rentIncrease[incentiveIndex];
    const selectedBenefit = netBenefit[incentiveIndex];
    
    const reductionPercent = beforeControl.map((b, i) => ((b - afterControl[i]) / b) * 100);
    
    const filteredIndices = d2SelectedDistricts.length > 0 
      ? districts.map((d, i) => d2SelectedDistricts.includes(d) ? i : -1).filter(i => i >= 0)
      : districts.map((_, i) => i);
    
    const avgBefore = beforeControl.reduce((a, b) => a + b, 0) / beforeControl.length;
    const avgAfter = afterControl.reduce((a, b) => a + b, 0) / afterControl.length;
    const avgBurdenBefore = beforeBurden.reduce((a, b) => a + b, 0) / beforeBurden.length;
    const avgBurdenAfter = afterBurden.reduce((a, b) => a + b, 0) / afterBurden.length;
    
    const improvement = beforeBurden.map((b, i) => ((b - afterBurden[i]) / b) * 100);
    
    return (
      <>
        <div className="title-bar">
          <b>Tactical Decisions:&nbsp;</b> Smart Rent Control Implementation
        </div>
        
        <div className="grid grid-cols-12 gap-4">
          {/* Sidebar */}
          <div className="col-span-3">
            <div className="sidebar">
              <h3>Implementation Controls</h3>
              
              <div className="filter-group">
                <label className="filter-label">Select districts to analyze</label>
                <select 
                  multiple 
                  className="filter-select" 
                  style={{height: '100px'}}
                  value={d2SelectedDistricts}
                  onChange={(e) => setD2SelectedDistricts(Array.from(e.target.selectedOptions, o => o.value))}
                >
                  {districts.map(d => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>
              
              <div className="filter-group">
                <label className="filter-label">Incentive level for landlords</label>
                <select 
                  className="filter-select"
                  value={d2IncentiveLevel}
                  onChange={(e) => setD2IncentiveLevel(e.target.value)}
                >
                  {incentiveLevels.map(l => (
                    <option key={l} value={l}>{l}</option>
                  ))}
                </select>
              </div>
              
              <div className="filter-group">
                <label className="filter-label">Timeline (months): {d2Timeline}</label>
                <input 
                  type="range" 
                  min="1" 
                  max="12" 
                  value={d2Timeline}
                  onChange={(e) => setD2Timeline(parseInt(e.target.value))}
                  className="w-full"
                />
              </div>
              
              <hr className="my-4 border-gray-200" />
              
              <h4 className="text-sm font-medium mb-2">Additional Filters</h4>
              <div className="filter-group">
                <label className="filter-label">Tenant categories to analyze</label>
                <select 
                  multiple 
                  className="filter-select" 
                  style={{height: '80px'}}
                  value={d2TenantCategories}
                  onChange={(e) => setD2TenantCategories(Array.from(e.target.selectedOptions, o => o.value))}
                >
                  {tenantCategories.map(c => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
          
          {/* Main content */}
          <div className="col-span-9">
            <div className="grid grid-cols-2 gap-4">
              {/* KPIs */}
              <div className="chart-container">
                <div className="kpi-grid">
                  <div className="kpi-item">
                    <h5>Average Rent Price</h5>
                    <div className="kpi-value">{avgAfter.toFixed(1)} €/m²</div>
                    <div className="kpi-delta positive">-{(avgBefore - avgAfter).toFixed(1)} €/m²</div>
                  </div>
                  <div className="kpi-item">
                    <h5>Landlord Participation</h5>
                    <div className="kpi-value">{selectedParticipation}%</div>
                    <div className="kpi-delta positive">+{selectedParticipation}%</div>
                  </div>
                  <div className="kpi-item">
                    <h5>Affordability Impact</h5>
                    <div className="kpi-value">{avgBurdenAfter.toFixed(1)}%</div>
                    <div className="kpi-delta positive">-{(avgBurdenBefore - avgBurdenAfter).toFixed(1)}%</div>
                  </div>
                  <div className="kpi-item">
                    <h5>Implementation Priority</h5>
                    <div className="kpi-value">3</div>
                    <div className="text-xs">High Priority Districts</div>
                  </div>
                </div>
                <div className="mt-2 p-2 bg-gray-100 rounded text-sm">
                  <b>Selected: {d2IncentiveLevel}</b> | Participation: {selectedParticipation}% | Rent Increase: {selectedRentIncrease}% | Benefit: €{selectedBenefit.toLocaleString()}
                </div>
              </div>
              
              {/* Rent Price Impact Chart */}
              <div className="chart-container">
                <Plot
                  data={[
                    {
                      x: filteredIndices.map(i => districts[i]),
                      y: filteredIndices.map(i => beforeControl[i]),
                      type: 'bar',
                      name: 'Before Control',
                      marker: { color: '#ff7f0e' }
                    },
                    {
                      x: filteredIndices.map(i => districts[i]),
                      y: filteredIndices.map(i => afterControl[i]),
                      type: 'bar',
                      name: 'After Control',
                      marker: { color: '#2ca02c' }
                    },
                    {
                      x: filteredIndices.map(i => districts[i]),
                      y: filteredIndices.map(i => reductionPercent[i]),
                      type: 'scatter',
                      mode: 'lines+markers',
                      name: 'Reduction (%)',
                      yaxis: 'y2',
                      line: { color: 'red', width: 2 },
                      marker: { size: 6 }
                    }
                  ]}
                  layout={{
                    title: 'Rent Price Impact by District',
                    barmode: 'group',
                    yaxis: { title: 'Rent Price (€/m²)' },
                    yaxis2: { title: 'Reduction (%)', overlaying: 'y', side: 'right', range: [0, 25] },
                    height: 250,
                    margin: { l: 50, r: 50, t: 40, b: 60 },
                    legend: { orientation: 'h', y: 1.1 }
                  }}
                  config={{ displayModeBar: false }}
                  style={{ width: '100%' }}
                />
              </div>
              
              {/* Landlord Incentives Chart */}
              <div className="chart-container">
                <Plot
                  data={[
                    {
                      x: incentiveLevels,
                      y: participationRates,
                      type: 'bar',
                      name: 'Landlord Participation',
                      marker: { color: '#1f77b4' },
                      text: participationRates.map(r => `${r}%`),
                      textposition: 'auto'
                    },
                    {
                      x: incentiveLevels,
                      y: rentIncrease,
                      type: 'scatter',
                      mode: 'lines+markers',
                      name: 'Rent Increase',
                      yaxis: 'y2',
                      line: { color: 'red', width: 2 },
                      marker: { size: 8 }
                    }
                  ]}
                  layout={{
                    title: 'Landlord Participation & Incentives',
                    yaxis: { title: 'Participation Rate (%)' },
                    yaxis2: { title: 'Rent Increase (%)', overlaying: 'y', side: 'right', range: [0, 6] },
                    height: 250,
                    margin: { l: 50, r: 50, t: 40, b: 30 },
                    legend: { orientation: 'h', y: 1.1 },
                    shapes: [{
                      type: 'rect',
                      x0: incentiveIndex - 0.4,
                      x1: incentiveIndex + 0.4,
                      y0: 0,
                      y1: participationRates[incentiveIndex] + 5,
                      line: { color: 'blue', width: 2 },
                      fillcolor: 'rgba(0, 123, 255, 0.3)'
                    }]
                  }}
                  config={{ displayModeBar: false }}
                  style={{ width: '100%' }}
                />
              </div>
              
              {/* Tab view */}
              <div className="chart-container">
                <div className="tab-buttons">
                  {['Implementation Strategy', 'General Affordability', 'District Affordability'].map(tab => (
                    <button
                      key={tab}
                      className={`tab-button ${d2Tab === tab ? 'active' : ''}`}
                      onClick={() => setD2Tab(tab)}
                    >
                      {tab}
                    </button>
                  ))}
                </div>
                
                {d2Tab === 'Implementation Strategy' && (
                  <Plot
                    data={[{
                      x: [1, 1, 1.5, 2, 3, 3, 2.5, 2, 4, 4].filter((_, i) => filteredIndices.includes(i)),
                      y: [9, 8, 8, 7, 6, 5, 7, 6, 5, 4].filter((_, i) => filteredIndices.includes(i)),
                      text: filteredIndices.map(i => districts[i]),
                      mode: 'markers+text',
                      type: 'scatter',
                      marker: { 
                        size: filteredIndices.map(i => beforeControl[i]),
                        color: ['High', 'High', 'High', 'Medium', 'Medium', 'Low', 'Medium', 'Medium', 'Low', 'Low']
                          .filter((_, i) => filteredIndices.includes(i))
                          .map(l => l === 'High' ? 'red' : l === 'Medium' ? 'orange' : 'green'),
                        opacity: 0.8,
                        line: { width: 1, color: 'black' }
                      },
                      textposition: 'top center'
                    }]}
                    layout={{
                      title: 'Implementation Strategy by District',
                      xaxis: { title: 'Timeline (months)' },
                      yaxis: { title: 'Priority Score' },
                      height: 200,
                      margin: { l: 50, r: 20, t: 40, b: 40 },
                      shapes: [{
                        type: 'line',
                        x0: d2Timeline,
                        x1: d2Timeline,
                        y0: 0,
                        y1: 10,
                        line: { color: 'blue', width: 2, dash: 'dot' }
                      }]
                    }}
                    config={{ displayModeBar: false }}
                    style={{ width: '100%' }}
                  />
                )}
                
                {d2Tab === 'General Affordability' && (
                  <Plot
                    data={[
                      {
                        x: tenantCategories.filter(c => d2TenantCategories.includes(c)),
                        y: beforeBurden.filter((_, i) => d2TenantCategories.includes(tenantCategories[i])),
                        type: 'bar',
                        name: 'Before',
                        marker: { color: '#d62728' },
                        text: beforeBurden.filter((_, i) => d2TenantCategories.includes(tenantCategories[i])).map(v => `${v.toFixed(1)}%`),
                        textposition: 'auto'
                      },
                      {
                        x: tenantCategories.filter(c => d2TenantCategories.includes(c)),
                        y: afterBurden.filter((_, i) => d2TenantCategories.includes(tenantCategories[i])),
                        type: 'bar',
                        name: 'After',
                        marker: { color: '#2ca02c' },
                        text: afterBurden.filter((_, i) => d2TenantCategories.includes(tenantCategories[i])).map(v => `${v.toFixed(1)}%`),
                        textposition: 'auto'
                      }
                    ]}
                    layout={{
                      title: 'Impact on Housing Affordability',
                      barmode: 'group',
                      yaxis: { title: '% Income on Rent', range: [0, 60] },
                      height: 200,
                      margin: { l: 50, r: 20, t: 40, b: 40 },
                      legend: { orientation: 'h', y: 1.1 }
                    }}
                    config={{ displayModeBar: false }}
                    style={{ width: '100%' }}
                  />
                )}
                
                {d2Tab === 'District Affordability' && (
                  <Plot
                    data={[
                      {
                        x: districtSubset,
                        y: youthBefore,
                        type: 'bar',
                        name: 'Youth Before',
                        marker: { color: '#ff9999' }
                      },
                      {
                        x: districtSubset,
                        y: youthAfter,
                        type: 'bar',
                        name: 'Youth After',
                        marker: { color: '#99ff99' }
                      },
                      {
                        x: districtSubset,
                        y: lowIncomeBefore,
                        type: 'bar',
                        name: 'Low-Income Before',
                        marker: { color: '#ffcc99' }
                      },
                      {
                        x: districtSubset,
                        y: lowIncomeAfter,
                        type: 'bar',
                        name: 'Low-Income After',
                        marker: { color: '#99ccff' }
                      }
                    ]}
                    layout={{
                      title: 'District-Specific Affordability Impact',
                      barmode: 'group',
                      yaxis: { title: '% Income on Rent' },
                      height: 200,
                      margin: { l: 50, r: 20, t: 40, b: 40 },
                      legend: { orientation: 'h', y: 1.1, font: { size: 9 } }
                    }}
                    config={{ displayModeBar: false }}
                    style={{ width: '100%' }}
                  />
                )}
              </div>
            </div>
            
            <div className="footer">
              Data Sources: Madrid Data Portal, CIS Survey 2014, El Confidencial (2024) | Settings: {d2IncentiveLevel} | Districts: {d2SelectedDistricts.length || 'All'}
            </div>
          </div>
        </div>
      </>
    );
  };

  const renderDashboard3 = () => {
    const { sankeyData, years, currentPropertyTax, socialImpact, districts, affordabilityImprovement, incentiveCost, implementationComplexity } = dashboardThreeData;
    
    const remainingBudget = 100 - d3IncentiveBudget;
    const rentReduction = -1440;
    const netGain = d3TaxSavings + rentReduction;
    
    const growthWithout = d3GrowthWithout / 100;
    const growthWith = d3GrowthWith / 100;
    
    const revenueWithout = years.map((_, t) => currentPropertyTax * Math.pow(1 + growthWithout, t));
    const revenueWith = years.map((_, t) => currentPropertyTax * Math.pow(1 + growthWith, t));
    const revenueDiff = revenueWith.map((v, i) => v - revenueWithout[i]);
    const cumulativeDiff = revenueDiff.reduce((a, b) => a + b, 0);
    
    const roi = (cumulativeDiff / (d3IncentiveBudget || 1)) * 100;
    const revenueGrowth = ((revenueWith[9] / revenueWithout[9]) - 1) * 100;
    
    // Simplified payback calculation
    let paybackPeriod = 0;
    let cumulative = 0;
    for (let i = 0; i < revenueDiff.length; i++) {
      cumulative += revenueDiff[i];
      if (cumulative >= d3IncentiveBudget) {
        paybackPeriod = i + 1;
        break;
      }
    }
    if (paybackPeriod === 0) paybackPeriod = 10;
    
    const roiRatio = affordabilityImprovement.map((a, i) => (a / incentiveCost[i]) * 100);
    
    const filteredIndices = d3SelectedDistricts.length > 0 
      ? districts.map((d, i) => d3SelectedDistricts.includes(d) ? i : -1).filter(i => i >= 0)
      : districts.map((_, i) => i);
    
    return (
      <>
        <div className="title-bar">
          <b>Analytical Insights:</b>&nbsp;Deep-Dive Financial Analysis
        </div>
        
        <div className="grid grid-cols-12 gap-4">
          {/* Sidebar */}
          <div className="col-span-3">
            <div className="sidebar">
              <h3>Analysis Controls</h3>
              
              <div className="filter-group">
                <label className="filter-label">Incentive Budget (% of total): {d3IncentiveBudget.toFixed(1)}%</label>
                <input 
                  type="range" 
                  min="20" 
                  max="40" 
                  step="0.1"
                  value={d3IncentiveBudget}
                  onChange={(e) => setD3IncentiveBudget(parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>
              
              <div className="filter-group">
                <label className="filter-label">Tax Savings per Landlord (€): {d3TaxSavings}</label>
                <input 
                  type="range" 
                  min="5000" 
                  max="9000" 
                  step="100"
                  value={d3TaxSavings}
                  onChange={(e) => setD3TaxSavings(parseInt(e.target.value))}
                  className="w-full"
                />
              </div>
              
              <div className="filter-group">
                <label className="filter-label">Base Growth Rate (%): {d3GrowthWithout.toFixed(1)}%</label>
                <input 
                  type="range" 
                  min="1" 
                  max="3" 
                  step="0.1"
                  value={d3GrowthWithout}
                  onChange={(e) => setD3GrowthWithout(parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>
              
              <div className="filter-group">
                <label className="filter-label">Enhanced Growth Rate (%): {d3GrowthWith.toFixed(1)}%</label>
                <input 
                  type="range" 
                  min={d3GrowthWithout + 0.1} 
                  max="5" 
                  step="0.1"
                  value={d3GrowthWith}
                  onChange={(e) => setD3GrowthWith(parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>
              
              <div className="filter-group">
                <label className="filter-label">Select Districts for Analysis</label>
                <select 
                  multiple 
                  className="filter-select" 
                  style={{height: '100px'}}
                  value={d3SelectedDistricts}
                  onChange={(e) => setD3SelectedDistricts(Array.from(e.target.selectedOptions, o => o.value))}
                >
                  {districts.map(d => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>
              
              <div className="filter-group">
                <label className="filter-label">District Analysis View</label>
                <select 
                  className="filter-select"
                  value={d3AnalysisView}
                  onChange={(e) => setD3AnalysisView(e.target.value)}
                >
                  <option value="Quadrant Analysis">Quadrant Analysis</option>
                  <option value="Heatmap Analysis">Heatmap Analysis</option>
                </select>
              </div>
            </div>
          </div>
          
          {/* Main content */}
          <div className="col-span-9">
            {/* KPIs */}
            <div className="grid grid-cols-4 gap-4 mb-4">
              <div className="metric-card text-center">
                <div className="metric-label">10-Year ROI</div>
                <div className="metric-value">{roi.toFixed(1)}%</div>
                <div className={`metric-delta ${roi > 100 ? 'positive' : 'negative'}`}>
                  {(roi - 100).toFixed(1)}% vs Initial
                </div>
              </div>
              <div className="metric-card text-center">
                <div className="metric-label">Payback Period</div>
                <div className="metric-value">{paybackPeriod.toFixed(1)} years</div>
                <div className={`metric-delta ${paybackPeriod < 5 ? 'positive' : 'negative'}`}>
                  {(5 - paybackPeriod).toFixed(1)} vs Target
                </div>
              </div>
              <div className="metric-card text-center">
                <div className="metric-label">Revenue Growth</div>
                <div className="metric-value">{revenueGrowth.toFixed(1)}%</div>
                <div className="metric-delta positive">+{revenueGrowth.toFixed(1)}% Boost</div>
              </div>
              <div className="metric-card text-center">
                <div className="metric-label">Affordability Improvement</div>
                <div className="metric-value">{socialImpact.toFixed(1)}%</div>
                <div className="metric-delta positive">+{(socialImpact - 20).toFixed(1)}% vs Baseline</div>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              {/* Sankey Diagram */}
              <div className="chart-container">
                <Plot
                  data={[{
                    type: 'sankey',
                    arrangement: 'snap',
                    node: {
                      pad: 15,
                      thickness: 20,
                      line: { color: 'black', width: 1.5 },
                      label: sankeyData.nodeLabels,
                      color: sankeyData.nodeColors
                    },
                    link: {
                      source: sankeyData.linkSources,
                      target: sankeyData.linkTargets,
                      value: [d3IncentiveBudget, remainingBudget, remainingBudget * 24/72.2, remainingBudget * 28.2/72.2, remainingBudget * 20/72.2],
                      color: sankeyData.linkColors
                    }
                  }]}
                  layout={{
                    title: 'Housing Budget Flow Analysis (€100M Total)',
                    height: 310,
                    margin: { l: 20, r: 20, t: 40, b: 60 },
                    font: { size: 12 },
                    annotations: [{
                      x: 0.5,
                      y: -0.15,
                      xref: 'paper',
                      yref: 'paper',
                      text: `<b>${d3IncentiveBudget.toFixed(1)}%</b> of total budget allocated`,
                      showarrow: false,
                      font: { size: 12 },
                      bgcolor: 'rgba(220, 239, 110, 0.8)',
                      bordercolor: '#3498db',
                      borderwidth: 1,
                      borderpad: 8
                    }]
                  }}
                  config={{ displayModeBar: false }}
                  style={{ width: '100%' }}
                />
              </div>
              
              {/* Waterfall Chart */}
              <div className="chart-container">
                <Plot
                  data={[{
                    type: 'waterfall',
                    orientation: 'v',
                    measure: ['relative', 'relative', 'total'],
                    x: ['Tax Savings', 'Rent Reduction', 'Net Gain'],
                    text: [`€${d3TaxSavings.toLocaleString()}`, `−€${Math.abs(rentReduction).toLocaleString()}`, `€${netGain.toLocaleString()}`],
                    textposition: 'auto',
                    y: [d3TaxSavings, rentReduction, null],
                    connector: { line: { color: 'grey' } },
                    decreasing: { marker: { color: '#d62728' } },
                    increasing: { marker: { color: '#2ca02c' } },
                    totals: { marker: { color: '#1f77b4' } }
                  }]}
                  layout={{
                    title: 'Landlord Financial Impact (Per Property)',
                    xaxis: { title: 'Financial Components' },
                    yaxis: { title: 'Amount (€)' },
                    height: 310,
                    margin: { l: 60, r: 30, t: 40, b: 40 },
                    showlegend: false
                  }}
                  config={{ displayModeBar: false }}
                  style={{ width: '100%' }}
                />
              </div>
            </div>
            
            <div className="grid grid-cols-3 gap-4 mt-4">
              {/* Chart selector and chart */}
              <div className="chart-container col-span-2">
                <div className="filter-group mb-2">
                  <select 
                    className="filter-select"
                    value={d3ChartType}
                    onChange={(e) => setD3ChartType(e.target.value)}
                  >
                    <option value="Long-term Projection">Long-term Projection</option>
                    <option value="Correlation Analysis">Correlation Analysis</option>
                    <option value="District Analysis">District Analysis</option>
                  </select>
                </div>
                
                {d3ChartType === 'Long-term Projection' && (
                  <Plot
                    data={[
                      {
                        x: years,
                        y: revenueWithout,
                        type: 'scatter',
                        mode: 'lines',
                        name: 'Without Program',
                        line: { color: 'steelblue', width: 3 }
                      },
                      {
                        x: years,
                        y: revenueWith,
                        type: 'scatter',
                        mode: 'lines',
                        name: 'With Program',
                        line: { color: 'green', width: 3 },
                        fill: 'tonexty',
                        fillcolor: 'rgba(0,128,0,0.1)'
                      },
                      {
                        x: years,
                        y: revenueDiff,
                        type: 'bar',
                        name: 'Annual Gain',
                        marker: { color: 'orange' },
                        yaxis: 'y2',
                        text: revenueDiff.map(v => `€${v.toFixed(1)}M`),
                        textposition: 'outside'
                      }
                    ]}
                    layout={{
                      title: 'Long-term Property Tax Revenue (2025–2034)',
                      xaxis: { title: 'Year' },
                      yaxis: { title: 'Tax Revenue (M €)', showgrid: true },
                      yaxis2: { title: 'Extra Gain (M €)', overlaying: 'y', side: 'right', range: [0, Math.max(...revenueDiff) * 1.6] },
                      height: 280,
                      margin: { l: 60, r: 60, t: 60, b: 40 },
                      legend: { orientation: 'h', y: 1.1 },
                      annotations: [{
                        x: 2030,
                        y: Math.max(...revenueDiff) * 1.3,
                        text: `<b>Cumulative 10Y Gain:</b><br>+€${cumulativeDiff.toFixed(1)}M`,
                        showarrow: false,
                        font: { size: 11, color: 'orange' },
                        bgcolor: 'white',
                        bordercolor: 'orange',
                        borderwidth: 1,
                        borderpad: 5
                      }]
                    }}
                    config={{ displayModeBar: false }}
                    style={{ width: '100%' }}
                  />
                )}
                
                {d3ChartType === 'Correlation Analysis' && (
                  <Plot
                    data={[
                      {
                        x: [0, 2000, 4000, 6000, 8000, 10000],
                        y: [5, 15, 25, 35, 50, 65],
                        type: 'scatter',
                        mode: 'markers',
                        name: 'Data Points',
                        marker: { size: 8, color: 'royalblue', line: { width: 1, color: 'black' } }
                      },
                      {
                        x: [0, 10000],
                        y: [5, 65],
                        type: 'scatter',
                        mode: 'lines',
                        name: 'Trendline',
                        line: { color: 'red', width: 2 }
                      }
                    ]}
                    layout={{
                      title: 'Incentives vs. Landlord Participation',
                      xaxis: { title: 'Tax Incentive (€)', tickformat: ',.0f' },
                      yaxis: { title: 'Participation Rate (%)' },
                      height: 280,
                      margin: { l: 60, r: 20, t: 40, b: 40 },
                      annotations: [
                        { x: 1000, y: 85, text: '<b>Correlation:</b> 0.85<br><b>R²:</b> 0.72', showarrow: false, bgcolor: 'white', bordercolor: 'black', borderwidth: 1 }
                      ]
                    }}
                    config={{ displayModeBar: false }}
                    style={{ width: '100%' }}
                  />
                )}
                
                {d3ChartType === 'District Analysis' && d3AnalysisView === 'Quadrant Analysis' && (
                  <Plot
                    data={[{
                      x: filteredIndices.map(i => incentiveCost[i]),
                      y: filteredIndices.map(i => affordabilityImprovement[i]),
                      text: filteredIndices.map(i => districts[i]),
                      mode: 'markers+text',
                      type: 'scatter',
                      marker: { 
                        size: filteredIndices.map(i => roiRatio[i] / 2),
                        color: filteredIndices.map(i => implementationComplexity[i]),
                        colorscale: 'Viridis',
                        line: { width: 1, color: 'DarkSlateGrey' },
                        sizemin: 10
                      },
                      textposition: 'top center'
                    }]}
                    layout={{
                      title: 'District Cost-Effectiveness Analysis',
                      xaxis: { title: 'Cost (€/unit)', range: [100, 260] },
                      yaxis: { title: 'Affordability Improvement (%)', range: [15, 35] },
                      height: 280,
                      margin: { l: 60, r: 20, t: 40, b: 40 },
                      shapes: [
                        { type: 'line', x0: 175, x1: 175, y0: 15, y1: 35, line: { color: 'gray', width: 1, dash: 'dash' } },
                        { type: 'line', x0: 100, x1: 260, y0: 23, y1: 23, line: { color: 'gray', width: 1, dash: 'dash' } }
                      ],
                      annotations: [
                        { x: 130, y: 32, text: '<b>High Impact<br>Low Cost</b>', showarrow: false, font: { size: 10, color: 'green' } },
                        { x: 220, y: 32, text: '<b>High Impact<br>High Cost</b>', showarrow: false, font: { size: 10, color: 'blue' } },
                        { x: 130, y: 18, text: '<b>Low Impact<br>Low Cost</b>', showarrow: false, font: { size: 10, color: 'orange' } },
                        { x: 220, y: 18, text: '<b>Low Impact<br>High Cost</b>', showarrow: false, font: { size: 10, color: 'red' } }
                      ]
                    }}
                    config={{ displayModeBar: false }}
                    style={{ width: '100%' }}
                  />
                )}
                
                {d3ChartType === 'District Analysis' && d3AnalysisView === 'Heatmap Analysis' && (
                  <Plot
                    data={[{
                      type: 'heatmap',
                      x: filteredIndices.map(i => districts[i]),
                      y: ['ROI Ratio', 'Cost (€)', 'Affordability (%)'],
                      z: [
                        filteredIndices.map(i => roiRatio[i]),
                        filteredIndices.map(i => incentiveCost[i]),
                        filteredIndices.map(i => affordabilityImprovement[i])
                      ],
                      colorscale: 'RdBu',
                      reversescale: true,
                      text: [
                        filteredIndices.map(i => roiRatio[i].toFixed(2)),
                        filteredIndices.map(i => `€${incentiveCost[i]}`),
                        filteredIndices.map(i => `${affordabilityImprovement[i]}%`)
                      ],
                      texttemplate: '%{text}',
                      textfont: { size: 10 }
                    }]}
                    layout={{
                      title: 'District Affordability vs. Costs Heatmap',
                      xaxis: { title: 'District', tickangle: -30 },
                      yaxis: { title: 'Metric' },
                      height: 280,
                      margin: { l: 100, r: 20, t: 40, b: 80 }
                    }}
                    config={{ displayModeBar: false }}
                    style={{ width: '100%' }}
                  />
                )}
              </div>
              
              {/* Insights Box */}
              <div className="insights-box">
                <h3>Analysis Insights</h3>
                <div className="insight-item">
                  <div className="insight-label">Program Payback:</div>
                  <div className="insight-value">Pays for itself in <b>{paybackPeriod.toFixed(1)} years</b></div>
                </div>
                <div className="insight-item">
                  <div className="insight-label">Revenue Impact:</div>
                  <div className="insight-value">Generates <b>€{cumulativeDiff.toFixed(1)}M</b> over 10 years</div>
                </div>
                <div className="insight-item">
                  <div className="insight-label">Budget Allocation:</div>
                  <div className="insight-value">Tax incentives are <b>{d3IncentiveBudget.toFixed(1)}%</b> of budget</div>
                </div>
                <div className="insight-item">
                  <div className="insight-label">Landlord Benefit:</div>
                  <div className="insight-value">Average gain of <b>€{netGain.toLocaleString()}</b> annually</div>
                </div>
              </div>
            </div>
            
            <div className="footer">
              Sources: Madrid Tax Revenue Reports, Landlord Survey 2023 | Budget: {d3IncentiveBudget.toFixed(1)}% | Growth: {d3GrowthWith.toFixed(1)}%
            </div>
          </div>
        </div>
      </>
    );
  };

  return (
    <main className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        {currentPage === 'dashboard1' && renderDashboard1()}
        {currentPage === 'dashboard2' && renderDashboard2()}
        {currentPage === 'dashboard3' && renderDashboard3()}
        
        <div className="nav-buttons">
          <button
            className="nav-button"
            disabled={currentPage === 'dashboard1'}
            onClick={() => {
              if (currentPage === 'dashboard3') setCurrentPage('dashboard2');
              else if (currentPage === 'dashboard2') setCurrentPage('dashboard1');
            }}
          >
            ⬅️ Previous
          </button>
          <span className="px-4 py-2 text-gray-500">
            {currentPage === 'dashboard1' && '1 / 3'}
            {currentPage === 'dashboard2' && '2 / 3'}
            {currentPage === 'dashboard3' && '3 / 3'}
          </span>
          <button
            className="nav-button"
            disabled={currentPage === 'dashboard3'}
            onClick={() => {
              if (currentPage === 'dashboard1') setCurrentPage('dashboard2');
              else if (currentPage === 'dashboard2') setCurrentPage('dashboard3');
            }}
          >
            Next ➡️
          </button>
        </div>
      </div>
    </main>
  );
}
