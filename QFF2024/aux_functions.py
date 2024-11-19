import requests
import os
import matplotlib.pyplot as plt
import numpy as np
import inspect
from qiskit import qasm2

import_statements = [
    "import numpy as np",          # Import with alias
    "import math",                 # Simple import
    "import pandas as pd",         # Another import with alias
    "from collections import Counter",  # Specific class import
    "from qiskit import QuantumCircuit",
    "from qiskit.quantum_info import Statevector",
    "from qiskit.primitives import StatevectorSampler",
    "from qiskit import qasm2",
    "from qiskit.visualization import plot_histogram",
    "from qiskit_ibm_runtime import SamplerV2 as Sampler",
    "from qiskit_ibm_runtime import QiskitRuntimeService",
    "from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager"
]
def plot_data(training_data, training_labels, test_data=None, test_labels=None):
    """
    Visualize the training data points and the test data point.

    Args:
        training_data (list of lists): Each sublist is a 2D point in the training data.
        training_labels (list): Labels corresponding to each point in the training data.
        test_data (list, optional): A 2D point representing the test data.
        test_label (str, optional): Label for the test data point.
    """
    # Extract unique labels for colors
    unique_labels = list(set(training_labels))
    colors = plt.cm.rainbow(np.linspace(0, 1, len(unique_labels)))
    label_color_map = dict(zip(unique_labels, colors))
    
    # Plot each point in training data
    for point, label in zip(training_data, training_labels):
        plt.scatter(point[0], point[1], color=label_color_map[label], label=label, s=100, alpha=0.7, edgecolors="k")
    
    # Plot each test data point if provided
    if test_data is not None:
        if test_labels is not None:
            for point, label in zip(test_data, test_labels):
                plt.scatter(point[0], point[1], color=label_color_map[label], label=label, marker='*', s=100, alpha=0.7, edgecolors="k")
        else:
            for i, point in enumerate(test_data):
                test_label = test_labels[i] if test_labels and i < len(test_labels) else "Test Data"
                plt.scatter(point[0], point[1], color="black", marker="*", s=150, label=test_label)
    
    # Determine max coordinate value from all points
    all_points = np.array(training_data)
    if test_data is not None:
        all_points = np.vstack([all_points, test_data])  # Add test data to the points

    min_coord = np.min(all_points)
    max_coord = np.max(all_points)
    
    # Add 10% padding to the range
    padding = 0.1 * (max_coord - min_coord)
    lower_limit = min_coord - padding
    upper_limit = max_coord + padding

    # Set axis limits with padding
    plt.xlim(lower_limit, upper_limit)
    plt.ylim(lower_limit, upper_limit)
    
    # Adding labels and legend
    plt.xlabel("Feature 1")
    plt.ylabel("Feature 2")
    plt.title("Training and Test Data Points")
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())
    plt.gca().set_aspect('equal', adjustable='box')
    plt.grid(True)
    plt.show()


def include_imports(import_statements, function_code):
    """
    Include specified import statements at the top of a function represented as a string.

    :param import_statements: List of import statements (e.g., ["import numpy as np", "import math"]).
    :param function_code: String containing the function code.
    :return: Updated function code with imports added.
    """
    try:
        # Combine import statements into a single string
        imports = "\n".join(import_statements)
        
        # Combine imports and function code
        updated_code = f"{imports}\n\n{function_code}" if imports else function_code
        
        return updated_code
    except Exception as e:
        raise RuntimeError(f"Failed to include imports: {e}")

def grade_answer(cell_id, answer):

    url = "http://127.0.0.1:5000/grade"
    email = os.environ['email']
    location = os.environ['location']
    payload = {
        "email": email,
        "cell_id": cell_id,
        "answer": answer,
        "location": location
    }
    response = requests.post(url, json=payload)
    
    return response.json()


def grade_answer_function(cell_id, answer):

    url = "http://158.227.112.208:5000/grade"
    email = os.environ['email']
    location = os.environ['location']
    answer_aux = inspect.getsource(answer)
    answer_aux = include_imports(import_statements, answer_aux)
    payload = {
        "email": email,
        "cell_id": cell_id,
        "answer": answer_aux,
        "location": location
    }
    response = requests.post(url, json=payload)
    
    return response.json()

def submit_answer_q1(answer):
    result = grade_answer_function("q1", answer)
    if result.get('correct'):
        print("Your answer is correct!")
    else:
        print("Your answer is incorrect. Try again.")

def submit_answer_q2(answer):
    result = grade_answer_function("q2", answer)
    if result.get('correct'):
        print("Your answer is correct!")
    else:
        print("Your answer is incorrect. Try again.")

def submit_answer_q3(answer):
    result = grade_answer_function("q3", answer)
    if result.get('correct'):
        print("Your answer is correct!")
    else:
        print("Your answer is incorrect. Try again.")

def submit_answer_q4(answer):
    result = grade_answer_function("q4", answer)
    if result.get('correct'):
        print("Your answer is correct!")
    else:
        print("Your answer is incorrect. Try again.")

def submit_answer_q5(answer):
    result = grade_answer_function("q5", answer)
    if result.get('correct'):
        print("Your answer is correct!")
    else:
        print("Your answer is incorrect. Try again.")

def submit_answer_q6(answer):
    result = grade_answer_function("q6", answer)
    if result.get('correct'):
        print("Your answer is correct!")
    else:
        print("Your answer is incorrect. Try again.")

def submit_answer_q7(answer, overlap):
    result = grade_answer_function("q7", answer)
    if overlap > 0.6 and overlap < 0.8 and result.get('correct'):
        print("Your answer is correct!")
    else:
        print("Your answer is incorrect. Try again.")

def submit_answer_q8(answer):
    result = grade_answer_function("q8", answer)
    if result.get('correct'):
        print("Your answer is correct!")
    else:
        print("Your answer is incorrect. Try again.")





