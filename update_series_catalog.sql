
-- Clear out the entire SeriesCatalog Table
use RushValley;
DELETE FROM  seriescatalog WHERE ValueCount = 0 or ValueCount is NULL;

-- Re-create the records in the SeriesCatalog Table
INSERT INTO seriescatalog (SiteID, SiteCode, SiteName, SiteType, VariableID, VariableCode, VariableName, Speciation,
	VariableUnitsID, VariableUnitsName, SampleMedium, ValueType, TimeSupport, TimeUnitsID, TimeUnitsName, DataType,
	GeneralCategory, MethodID, MethodDescription, SourceID, Organization, SourceDescription, Citation, QualityControlLevelID, 
	QualityControlLevelCode, BeginDateTime, EndDateTime, BeginDateTimeUTC, EndDateTimeUTC, ValueCount)
SELECT     dv.SiteID, s.SiteCode, s.SiteName, s.SiteType, dv.VariableID, v.VariableCode, 
           v.VariableName, v.Speciation, v.VariableUnitsID, u.UnitsName AS VariableUnitsName, v.SampleMedium, 
           v.ValueType, v.TimeSupport, v.TimeUnitsID, u1.UnitsName AS TimeUnitsName, v.DataType, 
           v.GeneralCategory, dv.MethodID, m.MethodDescription, dv.SourceID, so.Organization, 
           so.SourceDescription, so.Citation, dv.QualityControlLevelID, qc.QualityControlLevelCode, dv.BeginDateTime, 
           dv.EndDateTime, dv.BeginDateTimeUTC, dv.EndDateTimeUTC, dv.ValueCount 
FROM  (
SELECT SiteID, VariableID, MethodID, QualityControlLevelID, SourceID, MIN(LocalDateTime) AS BeginDateTime, 
           MAX(LocalDateTime) AS EndDateTime, MIN(DateTimeUTC) AS BeginDateTimeUTC, MAX(DateTimeUTC) AS EndDateTimeUTC, 
		   COUNT(DataValue) AS ValueCount
FROM datavalues
GROUP BY SiteID, VariableID, MethodID, QualityControlLevelID, SourceID) dv
           INNER JOIN sites s ON dv.SiteID = s.SiteID 
		   INNER JOIN variables v ON dv.VariableID = v.VariableID 
		   INNER JOIN units u ON v.VariableUnitsID = u.UnitsID 
		   INNER JOIN methods m ON dv.MethodID = m.MethodID 
		   INNER JOIN units u1 ON v.TimeUnitsID = u1.UnitsID 
		   INNER JOIN sources so ON dv.SourceID = so.SourceID 
		   INNER JOIN qualitycontrollevels qc ON dv.QualityControlLevelID = qc.QualityControlLevelID
GROUP BY   dv.SiteID, s.SiteCode, s.SiteName, s.SiteType, dv.VariableID, v.VariableCode, v.VariableName, v.Speciation,
           v.VariableUnitsID, u.UnitsName, v.SampleMedium, v.ValueType, v.TimeSupport, v.TimeUnitsID, u1.UnitsName, 
		   v.DataType, v.GeneralCategory, dv.MethodID, m.MethodDescription, dv.SourceID, so.Organization, 
		   so.SourceDescription, so.Citation, dv.QualityControlLevelID, qc.QualityControlLevelCode, dv.BeginDateTime,
		   dv.EndDateTime, dv.BeginDateTimeUTC, dv.EndDateTimeUTC, dv.ValueCount
ORDER BY   dv.SiteID, dv.VariableID, v.VariableUnitsID;