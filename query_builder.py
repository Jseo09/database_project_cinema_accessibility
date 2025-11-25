# query_builders.py

from config import (
    TABLE_THEATERS, COL_TID, COL_NAME, COL_CITY, COL_STATE, COL_STATUS,
    TABLE_FEAT, COL_WHEEL, COL_AL, COL_CC, COL_AD, COL_SRC, COL_CONF,
    TABLE_MOV, COL_MID, COL_MNAME,
    TABLE_SHOW, COL_SHOWID, COL_DT, COL_IS_CC, COL_IS_AD
)

def build_list_query(limit: int = 1000) -> str:
    return f"""
    SELECT {COL_TID} AS TID,
           {COL_NAME} AS Name,
           {COL_CITY} AS City,
           {COL_STATE} AS State,
           {COL_STATUS} AS Status
    FROM {TABLE_THEATERS}
    ORDER BY City, Name
    LIMIT {limit};
    """.strip()

def build_features_query() -> str:
    return f"""
    SELECT {COL_WHEEL}, {COL_AL}, {COL_CC}, {COL_AD}, {COL_SRC}, {COL_CONF}
    FROM {TABLE_FEAT}
    WHERE {COL_TID} = %s
    """.strip()

def build_movies_for_theater_query() -> str:
    return f"""
    SELECT s.{COL_SHOWID} AS show_id,
           COALESCE(m.{COL_MNAME}, '(Unknown)') AS movie_title,
           COUNT(*) AS num_shows
    FROM {TABLE_SHOW} s
    LEFT JOIN {TABLE_MOV} m
      ON m.{COL_MID} = s.{COL_SHOWID}
    WHERE s.{COL_TID} = %s
    GROUP BY s.{COL_SHOWID}, m.{COL_MNAME}
    ORDER BY movie_title;
    """.strip()

def build_showdates_for_movie_query() -> str:
    return f"""
    SELECT {COL_DT}, {COL_IS_CC}, {COL_IS_AD}
    FROM {TABLE_SHOW}
    WHERE {COL_TID} = %s AND {COL_SHOWID} = %s
    ORDER BY {COL_DT} ASC;
    """.strip()

def build_showtimes_query() -> str:
    return f"""
    SELECT {COL_DT},
           COALESCE(m.{COL_MNAME}, '(Unknown)') AS movie_title,
           {COL_IS_CC}, {COL_IS_AD}
    FROM {TABLE_SHOW} s
    LEFT JOIN {TABLE_MOV} m
      ON m.{COL_MID} = s.{COL_SHOWID}
    WHERE s.{COL_TID} = %s
    ORDER BY {COL_DT} ASC;
    """.strip()
