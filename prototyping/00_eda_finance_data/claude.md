# CLAUDE.md - Hennepin County Carbon Sequestration Financial Dashboard

## Project Overview

This React dashboard application provides interactive visualization and analysis tools for exploring Hennepin County's financial data related to natural resource management and carbon sequestration efforts. The dashboard connects financial expenditures with land use categories to help identify the most cost-effective approaches to carbon sequestration.

## Purpose and Goals

The dashboard serves as a decision support tool for the "Getting to Zero" project, helping stakeholders:

1. Understand program-level costs of operation per year
2. Link financial data to specific land use categories
3. Analyze cost-effectiveness of different carbon sequestration strategies
4. Make data-driven decisions about future investments in nature-based solutions

## Data Structure

The dashboard works with financial transaction data that includes:

- Fund information (e.g., Solid Waste)
- Department IDs (e.g., Natural Resources General)
- Account codes (e.g., Salaries, Services)
- Project identifiers (e.g., ES-Elm Creek WMC)
- Monetary amounts
- Date information
- Transaction details

## Core Features

### 1. Data Upload and Management
- CSV/Excel upload functionality
- Data preview and validation
- Option to save and manage multiple datasets

### 2. Interactive Visualizations
- Program expenditure breakdown by department and project
- Time series analysis of spending patterns
- Cost distribution across land use categories
- Comparative analysis between different carbon sequestration approaches

### 3. Financial Analysis Tools
- Dynamic filtering by department, project, date range
- Cost per acre calculations
- Personnel vs. operational cost breakdowns
- ROI metrics when paired with sequestration data

### 4. Linkage to Land Use
- Mapping between financial codes and land use categories
- Visualization of costs by ecosystem type (forests, wetlands, prairie)
- Integration with GIS data (if available)

### 5. Carbon Sequestration Insights
- Cost per ton of carbon sequestered calculations
- Comparison of different natural resource management strategies
- Scenario modeling for budget allocation

## Technical Implementation

### Frontend Architecture
- React.js for UI components
- Redux for state management
- Material-UI or Chakra UI for component styling
- D3.js or Recharts for custom visualizations
- React Router for navigation

### Data Processing
- Client-side data processing using JavaScript
- Server-side processing for larger datasets (optional)
- Data transformation utilities for connecting financial data to land use categories

### Visualization Components
- Sankey diagrams for fund flow visualization
- Interactive heatmaps for cost distribution
- Time-series charts for trend analysis
- GIS map integration (optional)

## User Personas

1. **County Financial Analysts** - Need detailed breakdowns of expenditures across programs
2. **Environmental Program Managers** - Need to understand cost-effectiveness of different approaches
3. **Policy Makers** - Need high-level insights to guide funding decisions
4. **Researchers** - Need to connect financial data with carbon sequestration outcomes

## Development Roadmap

### Phase 1: Core Dashboard
- Basic data upload and management
- Essential visualizations (bar charts, pie charts, line graphs)
- Simple filtering capabilities

### Phase 2: Advanced Analysis
- Enhanced visualization components
- Cost calculation algorithms
- Time series analysis tools
- Export functionality

### Phase 3: Integration
- Land use category mapping
- Carbon sequestration metrics integration
- Scenario modeling capabilities
- API connections to other county systems (if applicable)

## Design Principles

1. **Simplicity** - Focus on clear, intuitive interfaces that don't require extensive training
2. **Flexibility** - Allow users to explore data from multiple angles
3. **Performance** - Optimize for responsive handling of large datasets
4. **Accessibility** - Ensure the dashboard is usable by people with disabilities
5. **Responsiveness** - Works across desktop and tablet devices

## Getting Started for Developers

1. Clone the repository
2. Install dependencies using `npm install`
3. Start the development server with `npm start`
4. Run tests with `npm test`

## Data Privacy and Security

- The dashboard should be deployed on secure county infrastructure
- No personally identifiable information should be included in financial datasets
- User authentication required for access to sensitive financial information
- All data processing happens client-side to minimize data transfer risks

## Future Enhancements

- Machine learning models to predict future costs
- Automated report generation for stakeholders
- Integration with other county environmental monitoring systems
- Expanded GIS capabilities for spatial analysis of costs and benefits
