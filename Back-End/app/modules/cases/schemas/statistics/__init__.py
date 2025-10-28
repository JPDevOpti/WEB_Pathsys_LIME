# Statistics schemas module

# Dashboard
from .dashboard_statistics_schemas import (
    CasesByMonthResponse,
    CasesByMonthRequest,
    PathologistCasesByMonthRequest,
    DashboardOverviewResponse,
    PacientesMetrics,
    CasosMetrics,
    MetricsResponse,
    MesAnterior,
    OpportunityMetrics,
    OpportunityResponse,
)

# Tests
from .test_statistics_schemas import (
    TestStats,
    TestSummary,
    MonthlyTestPerformanceResponse,
    TestMainStats,
    TestProcessingTimes,
    TestPathologist,
    TestDetailsResponse,
    TestPathologistsResponse,
    TestOpportunityStats,
    TestOpportunitySummary,
    TestOpportunityResponse,
    TestMonthlyTrend,
    TestMonthlyTrendsResponse,
)

# Entities
from .entity_statistics_schemas import (
    EntityStats,
    EntitySummary,
    MonthlyEntityPerformanceResponse,
    BasicStats,
    ProcessingTimes,
    TopRequestedTest,
    EntityDetails,
    EntityDetailsResponse,
    PathologistEntityStats,
    EntityPathologistsResponse,
)

# Pathologists
from .pathologist_statistics_schemas import (
    PathologistPerformanceItem,
    PathologistMonthlyPerformanceResponse,
    PathologistEntityItem,
    PathologistEntitiesResponse,
    PathologistTestItem,
    PathologistTestsResponse,
    PathologistOpportunitySummary,
    PathologistMonthlyTrendItem,
    PathologistMonthlyTrendsResponse,
)