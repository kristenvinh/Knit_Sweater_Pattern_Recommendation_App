CREATE OR REPLACE VIEW `knitwear-app.ravelry_data.v_enriched_pattern_descriptions` AS
SELECT
  ID,
  name,
  CONCAT(
    'This sweater is named ', IFNULL(name, 'Unknown'), '. ',
    'It is knit using ', IFNULL(yarn_weight, 'an unspecified'), ' weight yarn. ',
    'It has the following attributes: ', IFNULL(ARRAY_TO_STRING(Attributes, ', '), 'none specified'), '. ',
    'Pattern Description: ', IFNULL(notes, 'No description provided.')
  ) AS enriched_description
FROM 
  `knitwear-app.ravelry_data.detail_data`;