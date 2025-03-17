from .dbtest import (
    DbTest,
    dbconnect
)

import os
from psycopg2.extras import (
    RealDictCursor,
    RealDictRow
)


PATH_TO_SQL_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "sql"
    )
)

class TestExample(DbTest):
    @dbconnect
    def test_select_organizations(self, conn):
        self.load_fixtures(
            conn,
            os.path.join(PATH_TO_SQL_DIR, "organizations.sql")
        )

        sql = """
        SELECT * FROM organizations;
        """
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            organizations = cur.fetchall()

            assert len(organizations) == 7

    @dbconnect
    def test_count_the_number_of_subordinates(self, conn):
        self.load_fixtures(
            conn,
            os.path.join(PATH_TO_SQL_DIR, "organizations.sql")
        )

        sql = """
        SELECT
            COUNT(cust.customer_organization_id) AS subordinates_count,
            org.id
        FROM
            organizations org
            LEFT JOIN enterprise_sales_enterprise_customers cust ON org.id = cust.sales_organization_id
        GROUP BY
            org.id
        ORDER BY
            org.id;
        """
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            actual = cur.fetchall()
            print(actual)
            assert len(actual) == 7
            assert actual == [
                RealDictRow(**{
                    "subordinates_count": 0,
                    "id": 1,
                })
                , RealDictRow(**{
                    "subordinates_count": 4,
                    "id": 2,
                })
                , RealDictRow(**{
                    "subordinates_count": 0,
                    "id": 3,
                })
                , RealDictRow(**{
                    "subordinates_count": 0,
                    "id": 4,
                })
                , RealDictRow(**{
                    "subordinates_count": 0,
                    "id": 5,
                })
                , RealDictRow(**{
                    "subordinates_count": 1,
                    "id": 6,
                })
                , RealDictRow(**{
                    "subordinates_count": 0,
                    "id": 7,
                })
            ]

    @dbconnect
    def test_calculate_center_of_each_segment(self, conn):
        self.load_fixtures(
            conn,
            os.path.join(PATH_TO_SQL_DIR, "japan_segments.sql")
        )

        sql = """
        SELECT
            id,
            ST_X (ST_Centroid (bounds)) AS longitude,
            ST_Y (ST_Centroid (bounds)) AS latitude
        FROM
            japan_segments
        ORDER BY
            SPLIT_PART (id, '_', 1),
            CAST(SPLIT_PART (id, '_', 2) AS INTEGER);
        """
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            actual = cur.fetchall()
            print(actual)
            assert len(actual) == 10
            assert actual == [
                RealDictRow(**{
                    "id": "KAGOSHIMA_1",
                    "longitude": 130.642228315775,
                    "latitude": 30.7045454545455,
                })
                , RealDictRow(**{
                    "id": "KAGOSHIMA_2",
                    "longitude": 130.694183864916,
                    "latitude": 30.7045454545455,
                })
                , RealDictRow(**{
                    "id": "KAGOSHIMA_3",
                    "longitude": 130.746139414057,
                    "latitude": 30.7045454545455,
                })
                , RealDictRow(**{
                    "id": "KAGOSHIMA_4",
                    "longitude": 129.707028431231,
                    "latitude": 30.75,
                })
                , RealDictRow(**{
                    "id": "KAGOSHIMA_5",
                    "longitude": 129.758983980373,
                    "latitude": 30.75,
                })
                , RealDictRow(**{
                    "id": "KAGOSHIMA_6",
                    "longitude": 129.810939529514,
                    "latitude": 30.75,
                })
                , RealDictRow(**{
                    "id": "KAGOSHIMA_7",
                    "longitude": 129.862895078655,
                    "latitude": 30.75,
                })
                , RealDictRow(**{
                    "id": "KAGOSHIMA_8",
                    "longitude": 129.914850627797,
                    "latitude": 30.75,
                })
                , RealDictRow(**{
                    "id": "KAGOSHIMA_9",
                    "longitude": 129.966806176937,
                    "latitude": 30.75,
                })
                , RealDictRow(**{
                    "id": "KAGOSHIMA_10",
                    "longitude": 130.018761726079,
                    "latitude": 30.75,
                })
            ]

    @dbconnect
    def test_segments_using_geojson_boundary(self, conn):
        self.load_fixtures(
            conn,
            os.path.join(PATH_TO_SQL_DIR, "japan_segments.sql")
        )

        sql = """
        SELECT
            id
        FROM
            japan_segments
        WHERE
            ST_Intersects (
                bounds,
                ST_SetSRID (
                    ST_GeomFromGeoJSON (
                        '{
                            "type": "Polygon",
                            "coordinates": [[
                                [130.6, 30.6],
                                [130.8, 30.6],
                                [130.8, 30.8],
                                [130.6, 30.8],
                                [130.6, 30.6]
                            ]]
                        }'
                    ),
                    4326
                )
            )
        ORDER BY
            id;
        """
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            actual = cur.fetchall()
            print(actual)
            assert len(actual) == 3
            assert actual == [
                RealDictRow(**{
                    "id": "KAGOSHIMA_1",
                })
                , RealDictRow(**{
                    "id": "KAGOSHIMA_2",
                })
                , RealDictRow(**{
                    "id": "KAGOSHIMA_3",
                })
            ]
