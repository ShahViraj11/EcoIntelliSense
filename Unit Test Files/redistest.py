import redis
import json
from redis.commands.json.path import Path
import redis.commands.search.aggregation as aggregations
import redis.commands.search.reducers as reducers
from redis.commands.search.field import TextField, NumericField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import NumericFilter, Query
import apikeys

r = redis.StrictRedis(
  host='redis-19241.c1.us-central1-2.gce.cloud.redislabs.com',
  port=19241,
  password=apikeys.redis_password,)

def add_project(user_id, project_name, project_info):
    # Convert project_info to JSON for storage
    project_info_json = json.dumps(project_info)

    # Set the project information in Redis
    r.hset(f'user:{user_id}:projects', project_name, project_info_json)

def get_project_info(user_id, project_name):
    # Get the project information from Redis
    project_info_json = r.hget(f'user:{user_id}:projects', project_name)

    # Convert JSON back to Python dictionary
    project_info = json.loads(project_info_json) if project_info_json else None

    return project_info

# Example usage:
user_id = "123"
project_name1 = "project1"
project_info1 = {"description": "This is project 1", "status": "ongoing"}

project_name2 = "project2"
project_info2 = {"description": "This is project 2", "status": "completed"}

# Add projects for a user
add_project(user_id, project_name1, project_info1)
add_project(user_id, project_name2, project_info2)

# Retrieve project information
retrieved_info1 = get_project_info(user_id, project_name1)
retrieved_info2 = get_project_info(user_id, project_name2)

print("Retrieved Project 1 Info:", retrieved_info1)
print("Retrieved Project 2 Info:", retrieved_info2)
