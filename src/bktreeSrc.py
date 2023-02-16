import pandas as pd
from pybktree import BKTree
from geopy.distance import geodesic
import Levenshtein

# Define a class to compute the Levenshtein distance between two strings
class LevenshteinDistance:
    def __call__(self, itemX, itemY):
        return Levenshtein.distance(itemX[1], itemY[1])

# Read the input data from a CSV file
def read_data(filePath):
    return pd.read_csv(filePath)

# Build a BK tree of names from the input data
def create_name_tree(data):
    # Create a new BK tree using the Levenshtein distance function
    name_tree = BKTree(LevenshteinDistance())

    # Add each point's name to the tree
    for index, row in data.iterrows():
        name_tree.add((index, row['name']))

    return name_tree


# Check which points are similar to each other based on their names and geographic locations
def check_similarity(name_tree, data, maxDistance, maxEditDistance):
    # Create a list to keep track of whether each point is similar to another point
    is_similar = [0] * len(data)

    # A helper function to mark two points as similar
    def markSimilarPoints(ptIndex):
        # Check the edit distance between this name and all other names in the tree
        pairs = name_tree.find((ptIndex, data['name'][ptIndex]), maxEditDistance)
        for j, _ in pairs[1:]:
            # check the geographic distance between the two points
            distance = geodesic((data['latitude'][ptIndex], data['longitude'][ptIndex]),
                                (data['latitude'][j], data['longitude'][j])).meters
            if distance <= maxDistance:
                is_similar[ptIndex] = 1
                is_similar[j] = 1
    
    # Loop over each row of data and check it has any similar points
    for ptIndex in range(len(data)):
        if not is_similar[ptIndex]:
            markSimilarPoints(ptIndex)    
    
    return is_similar

# Add the 'isSimilar' column to the data frame
def add_similarity_column(data, is_similar):
    data['isSimilar'] = is_similar
    return data


# Main function that reads the input data, checks for similar points
# and saves the result to a CSV file
def locate_similar_points(filePath, maxDistance, maxEditDistance):
    data = read_data(filePath)

    name_tree = create_name_tree(data)
    is_similar = check_similarity(name_tree, data, maxDistance, maxEditDistance)
    data = add_similarity_column(data, is_similar)

    return data


if __name__ == '__main__':
    newData = locate_similar_points('../assignment_data.csv', 200, 5)
    newData.to_csv('../bkTreeResult.csv')
