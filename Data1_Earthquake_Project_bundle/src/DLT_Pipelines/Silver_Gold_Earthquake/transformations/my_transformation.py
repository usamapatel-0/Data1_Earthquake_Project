import dlt
from pyspark.sql.functions import *

catalog_name = spark.conf.get("catalog_name")


@dlt.table(
    name="earthquake_summary",
    comment="Overall earthquake summary"
)
def earthquake_summary():

    df = spark.read.table(
        f"{catalog_name}.silver.earthquake_data_final_silver"
    )

    return df.select(
        count("*").alias("total_earthquakes"),
        round(avg("mag"), 2).alias("avg_magnitude"),
        max("mag").alias("max_magnitude"),
        sum(when(col("tsunami") == 1, 1).otherwise(0)).alias("tsunami_events")
    )


@dlt.table(
    name="earthquake_daily",
    comment="Daily earthquake statistics"
)
def earthquake_daily():

    df = spark.read.table(
        f"{catalog_name}.silver.earthquake_data_final_silver"
    )

    return (
        df.groupBy(to_date("time").alias("earthquake_date"))
        .agg(
            count("*").alias("total_events"),
            round(avg("mag"), 2).alias("avg_magnitude"),
            max("mag").alias("max_magnitude")
        )
        .orderBy("earthquake_date")
    )


@dlt.table(
    name="magnitude_distribution",
    comment="Magnitude category distribution"
)
def magnitude_distribution():

    df = spark.read.table(
        f"{catalog_name}.silver.earthquake_data_final_silver"
    )

    return (
        df.withColumn(
            "magnitude_category",
            when(col("mag") < 2, "Minor")
            .when(col("mag") < 4, "Light")
            .when(col("mag") < 6, "Moderate")
            .otherwise("Strong")
        )
        .groupBy("magnitude_category")
        .agg(
            count("*").alias("earthquake_count")
        )
        .orderBy(desc("earthquake_count"))
    )


@dlt.table(
    name="top_locations",
    comment="Top earthquake locations"
)
def top_locations():

    df = spark.read.table(
        f"{catalog_name}.silver.earthquake_data_final_silver"
    )

    return (
        df.groupBy("place")
        .agg(
            count("*").alias("earthquake_count"),
            round(avg("mag"), 2).alias("avg_magnitude"),
            max("mag").alias("max_magnitude")
        )
        .orderBy(desc("earthquake_count"))
        .limit(20)
    )


@dlt.table(
    name="tsunami_summary",
    comment="Tsunami event summary"
)
def tsunami_summary():

    df = spark.read.table(
        f"{catalog_name}.silver.earthquake_data_final_silver"
    )

    return (
        df.groupBy("tsunami")
        .agg(
            count("*").alias("total_events")
        )
        .orderBy("tsunami")
    )


@dlt.table(
    name="status_summary",
    comment="Earthquake status summary"
)
def status_summary():

    df = spark.read.table(
        f"{catalog_name}.silver.earthquake_data_final_silver"
    )

    return (
        df.groupBy("status")
        .agg(
            count("*").alias("total_events")
        )
        .orderBy(desc("total_events"))
    )