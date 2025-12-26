import graphene


## Elo chart
class XYPointType(graphene.ObjectType):
    x = graphene.Float(required=True)
    y = graphene.Float(required=True)


class EloDatasetType(graphene.ObjectType):
    label = graphene.String(required=True)
    backgroundColor = graphene.String(required=True)
    borderColor = graphene.String(required=True)
    data = graphene.List(XYPointType, required=True)


class EloChartDataType(graphene.ObjectType):
    datasets = graphene.List(EloDatasetType, required=True)


class EloChartType(graphene.ObjectType):
    title = graphene.String(required=True)
    lastUpdated = graphene.Float()
    data = graphene.Field(EloChartDataType, required=True)


## Winrate By Time
class ChartDataLabelsOptionsType(graphene.ObjectType):
    align = graphene.String(required=True)
    anchor = graphene.String(required=True)


class ChartDatasetType(graphene.ObjectType):
    label = graphene.String(required=True)
    data = graphene.List(graphene.Int, required=True)
    backgroundColor = graphene.String(required=True)
    extraLabels = graphene.List(graphene.String, required=True)
    datalabels = graphene.Field(ChartDataLabelsOptionsType, required=True)


class ChartDataType(graphene.ObjectType):
    labels = graphene.List(graphene.String, required=True)
    datasets = graphene.List(ChartDatasetType, required=True)


class WinrateChartType(graphene.ObjectType):
    title = graphene.String(required=True)
    data = graphene.Field(ChartDataType, required=True)


## Race winrate
class RaceOutcomeBreakdownType(graphene.ObjectType):
    wins = graphene.Int(required=True)
    losses = graphene.Int(required=True)
    ties = graphene.Int(required=True)
    crashes = graphene.Int(required=True)
    played = graphene.Int(required=True)

    winRate = graphene.Float(required=True)
    lossRate = graphene.Float(required=True)
    tieRate = graphene.Float(required=True)
    crashRate = graphene.Float(required=True)


class RaceMatchupBreakdownType(graphene.ObjectType):
    zerg = graphene.Field(RaceOutcomeBreakdownType, required=True)
    protoss = graphene.Field(RaceOutcomeBreakdownType, required=True)
    terran = graphene.Field(RaceOutcomeBreakdownType, required=True)
    random = graphene.Field(RaceOutcomeBreakdownType, required=True)
