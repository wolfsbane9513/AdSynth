# AdSynth Frontend Development Prompt

## Project Overview
Create a modern, responsive frontend for the AdSynth AI Ad Generator using React and Chakra UI. The application will interface with the existing backend API running on localhost:8000.

## Tech Stack
- React (with TypeScript)
- Chakra UI for component library
- React Router for navigation
- React Query for API state management
- Axios for API requests
- React Hook Form for form handling
- Zod for form validation

## Base Configuration
- API Base URL: `http://localhost:8000`
- Authentication: Bearer token stored in localStorage
- Theme: Light/Dark mode support using Chakra UI's theme system

## Core Features

### Authentication System
1. **Login Page** (`/login`)
   - Clean login form with email/password inputs
   - Remember me checkbox
   - Forgot password link
   - Registration link
   - Error handling display
   - Loading states

2. **Registration Page** (`/register`)
   - Username input
   - Email input
   - Password input with strength indicator
   - Password confirmation
   - Terms of service checkbox
   - Loading states

3. **Profile Management** (`/profile`)
   - View/Edit user information
   - Change password functionality
   - Email update capability

### Campaign Management

1. **Campaign Dashboard** (`/campaigns`)
   - Grid/List view of campaigns
   - Campaign cards showing:
     - Campaign name
     - Description
     - Creation date
     - Status
   - Quick action buttons
   - Sorting and filtering options
   - Pagination

2. **Campaign Creation** (`/campaigns/new`)
   - Multi-step form with:
     - Basic Information
       - Campaign name
       - Description
     - Product Details
       - Product name
       - Product description
     - Target Audience
       - Audience description
       - Key use cases
     - Campaign Goals
   - Progress indicator
   - Save draft functionality

3. **Campaign Details** (`/campaigns/:id`)
   - Campaign overview
   - Generated ad scripts list
   - Performance metrics
   - Edit campaign button
   - Generate new ad button

### Ad Script Generation

1. **Generation Interface** (`/campaigns/:id/generate`)
   - Provider selection (OpenAI, Claude, Groq)
   - Model selection based on provider
   - Generation settings
   - Real-time generation progress
   - Stream output option

2. **Ad Script Management** (`/campaigns/:id/scripts`)
   - List of generated scripts
   - Filter by date/provider
   - Compare scripts side by side
   - Export functionality
   - Edit capability

## Reusable Components

### Layout Components
1. **AppShell**
   - Responsive sidebar
   - Top navigation bar
   - User menu
   - Theme toggle
   - Breadcrumbs

2. **PageContainer**
   - Consistent padding/margins
   - Responsive breakpoints
   - Loading states

### UI Components
1. **ActionButton**
   - Loading states
   - Different variants (primary, secondary, danger)
   - Icon support

2. **FormFields**
   - Input with validation
   - Select with search
   - Textarea with character count
   - File upload

3. **DataDisplay**
   - Tables with sorting/filtering
   - Cards with hover effects
   - Stats cards
   - Charts/Graphs

4. **Feedback**
   - Toast notifications
   - Alert dialogs
   - Progress indicators
   - Loading spinners

## API Integration

### Authentication Endpoints
```typescript
interface AuthAPI {
  login: (username: string, password: string) => Promise<TokenResponse>;
  register: (data: RegisterData) => Promise<UserResponse>;
  refreshToken: (token: string) => Promise<TokenResponse>;
  getProfile: () => Promise<UserResponse>;
  updateProfile: (data: UpdateProfileData) => Promise<UserResponse>;
}
```

### Campaign Endpoints
```typescript
interface CampaignAPI {
  list: () => Promise<Campaign[]>;
  create: (data: CampaignData) => Promise<Campaign>;
  get: (id: string) => Promise<Campaign>;
  update: (id: string, data: CampaignData) => Promise<Campaign>;
}
```

### Ad Script Endpoints
```typescript
interface AdScriptAPI {
  generate: (data: GenerateData) => Promise<AdScript>;
  list: (campaignId?: string) => Promise<AdScript[]>;
  get: (id: string) => Promise<AdScript>;
}
```

## State Management
- Use React Query for server state
- Context API for global UI state
- Local state for component-specific data

## Error Handling
- Global error boundary
- API error interceptors
- Form validation errors
- Network error handling
- Retry mechanisms

## Loading States
- Skeleton loaders for content
- Spinner for actions
- Progress bars for generation
- Disabled states for forms

## Responsive Design
- Mobile-first approach
- Breakpoints:
  - sm: 30em (480px)
  - md: 48em (768px)
  - lg: 62em (992px)
  - xl: 80em (1280px)

## Accessibility
- ARIA labels
- Keyboard navigation
- Focus management
- Color contrast compliance
- Screen reader support

## Performance Considerations
- Code splitting
- Lazy loading
- Image optimization
- Caching strategies
- Debounced inputs

## Security Measures
- Token management
- XSS prevention
- CSRF protection
- Secure data storage
- Input sanitization

## Testing Requirements
- Unit tests for components
- Integration tests for flows
- E2E tests for critical paths
- Accessibility testing
- Performance testing

## Documentation
- Component documentation
- API integration guide
- State management patterns
- Testing guide
- Deployment instructions

This prompt provides a comprehensive guide for implementing the frontend of our AdSynth application. The implementation should follow modern React best practices and maintain consistency with the provided backend API documentation.