from drafter import *
from dataclasses import dataclass

set_website_title("Lab Yield Tracker")

"""
Lab Yield Tracker
A Drafter website that records lab experiments, calculates
percent yield, and keeps a history so results can be compared
and likely errors can be spotted.
"""

set_site_information(
    author = "William Anater",
    description = "Records lab experiments, calculates percent yield, and keeps a history for comparing results.",
    sources = "Built with the Drafter library.",
    planning = "See the brainstorming and design worksheets in this repository.",
    links = "https://will-anater.github.io/percent-yield-site/"
)

set_website_framed(False)

@dataclass
class Experiment:
    """One saved lab experiment and its calculated percent yield."""
    name: str
    theoretical_yield: float
    actual_yield: float
    percent_yield: float


@dataclass
class State:
    """Everything the website remembers between pages.
    the fields are, respectively:
    list of every saved experiemnt,
    shown on the form when the input is bad,
    most recent result,
    returns "All", "Good", "Low", or "Over 100%"."""
    experiments: list[Experiment]
    error_message: str
    latest_percent: float
    filter_choice: str


def label_for(percent: float) -> str:
    """
    This is a helper function that gives a quality label
    to a percent yield, i.e. "Over 100%", "Good", or "Low".
    """
    if percent > 100:
        return "Over 100%"
    elif percent >=70:
        return "Good"
    else:
        return "Low"

def calculate_percent_yield(theoretical_yield: float, actual_yield: float) -> float:
    """ A helper function that returns the actual yield
    divided by the the theoretical yield as a percent,
    rounded to 1 decimal."""
    return round(actual_yield / theoretical_yield * 100, 1)


def check_inputs(name: str, theoretical: str, actual: str) -> str:
    """ Returns an error message for bad input form,
    or an empty string if the input is fine."""
    if name.strip() == "" or theoretical.strip() == "" or actual.strip() == "":
        return "Please fill in every box."
    
    """ try/except (not covered in class): float() raises
    ValueError when the text is not a number, and this code catches this
    instead of letting the site crash."""
    
    try:
        theoretical_yield = float(theoretical)
        actual_yield = float(actual)
    except ValueError:
        return "Yields must be numbers, like 12.5."
    
    if theoretical_yield <= 0 or actual_yield < 0:
        return "Theoretical yield must be greater than 0, and actual yield cannot be negative."
    return ""
    

@route
def index(state: State) ->Page:
    """ Shows the home page with links to the other pages."""
    return Page(state, [
        Header("Lab Yield Tracker"),
        "Record your lab experiments, calculate percent yield, and compare your results.",
        LineBreak(),
        Button("New Experiment", new_experiment),
        Button("View History", history),
        Button("Help", help_page),
    ])


@route
def new_experiment(state: State) -> Page:
    """ Shows the form for entering a new experiment, with
    any error message."""
    content = [
        Header("New Experiment"),
        "Experiment name:",
        TextBox("name"),
        LineBreak(),
        "Theoretical yield (grams):",
        TextBox("theoretical"),
        LineBreak(),
        "Actual yield (grams):",
        TextBox("actual"),
        LineBreak(),
    ]
    
    if state.error_message != "":
        content.append(state.error_message)
        content.append(LineBreak())
    content.append(Button("Calculate", save_experiment))
    content.append(Link("Home", index))
    return Page(state, content)


@route
def save_experiment(state: State, name: str, theoretical: str, actual: str) -> Page:
    """ Checks the form of input, saves a new Experiment,
    and shows its results."""
    error = check_inputs(name, theoretical, actual)
    if error != "":
        state.error_message = error
        return new_experiment(state)
    
    percent = calculate_percent_yield(float(theoretical),
float(actual))
    state.experiments.append(Experiment(name.strip(),
float(theoretical), float(actual), percent))
    state.latest_percent = percent
    state.error_message = ""
    return result(state)


@route
def result(state: State) -> Page:
    """ Show the latest percent yield with a message about
    what it means."""
    content = [
        Header("Result"),
        "Percent yield: " + str(state.latest_percent) + "%",
        LineBreak(),
    ]
    
    if state.latest_percent > 100:
        content.append("Warning: a yield over 100% usually means a measurement error, or a wet or impure product.")
    elif state.latest_percent >= 70:
        content.append("This is a good yield.")
    else:
        content.append("This yield is low. Check for lost product or an incomplete reaction.")
    
    content.append(LineBreak())
    content.append(Button("Add Another", new_experiment))
    content.append(Button("History", history))
    return Page(state, content)


@route
def history(state: State) -> Page:
    """ Shows every saved experiment that matches teh filter,
    with an averave."""
    content = [
        Header("History"),
        "Show:",
        SelectBox("choice",["All", "Good", "Low", "Over 100%"], state.filter_choice),
        Button("Apply Filter", apply_filter),
        HorizontalRule(),
    ]
    
    if len(state.experiments) == 0:
        content.append("No experiments yet. Add one to get started.")
    else:
        total = 0.0
        shown = 0
        """ Loops over the list of Experiment instances stored in the State."""
        for position in range(len(state.experiments)):
            experiment = state.experiments[position]
            label = label_for(experiment.percent_yield)
            if state.filter_choice == "All" or state.filter_choice == label:
                """ Argument (not covered in class) sends the hidden positions
                of this experiment to delete_experiment when the button is pressed."""
                content.append(experiment.name + ": " + str(experiment.percent_yield) + "% (" + label + ")")
                content.append(Button("Delete", delete_experiment, Argument("position", position)))
                content.append(LineBreak())
                total += experiment.percent_yield
                shown += 1
    
        if shown > 0:
            content.append("Average of shown experiments: " + str(round(total / shown, 1)) + "%")
        else:
            content.append("No experiments match this filter.")
    
    content.append(LineBreak())
    content.append(Link("Home", index))
    return Page(state, content)


@route
def apply_filter(state: State, choice: str) -> Page:
    """ Takes the filter selected by the user,
    then shows the history page."""
    state.filter_choice = choice
    return history(state)


@route
def delete_experiment(state: State, position: int, choice: str = "") -> Page:
    """Removes the experiment at the given position,
    then shows the history page."""
    """ "choice" has a default value (not covered in class)
    becuase of the select box. Value is sent along
    with every button on the history page, but it is not used."""
    if 0 <= position < len(state.experiments):
        state.experiments.pop(position)
    return history(state)


@route
def help_page(state: State) -> Page:
    """ Explains percent yield and how the history labels work."""
    return Page(state, [
        Header("Help"),
        "Percent yield = actual yield / theoretical yield * 100.",
        LineBreak(),
        "Theoretical yield is the most product the reaction could make. Actual yield is what you collected.",
        LineBreak(),
        "A result over 100% usually means a measurement mistake, or a product that was still wet or impure.",
        LineBreak(),
        "On the history page, Good means 70% or more, and Low means under 70%.",
        LineBreak(),
        Button("Home", index),
    ])


"""assert_equal tests"""


def fresh_state() -> State:
    """A helper function that makes an empty State for unit tests."""
    return State([], "", 0.0, "All")


def sample_state(filter_choice: str) -> State:
    """A helper function that makes a State holding
    one saved experiment (80% yield) for unit tests."""
    return State([Experiment("Test", 10.0, 8.0, 80.0)], "", 0.0, filter_choice)


assert_equal(label_for(120.0), "Over 100%")
assert_equal(label_for(85.0), "Good")
assert_equal(label_for(70.0), "Good")
assert_equal(label_for(40.0), "Low")


assert_equal(calculate_percent_yield(10.0, 8.0), 80.0)
assert_equal(calculate_percent_yield(3.0, 1.0), 33.3)
assert_equal(calculate_percent_yield(10.0, 12.5), 125.0)

assert_equal(check_inputs("", "10", "8"), "Please fill in every box.")
assert_equal(check_inputs("Test", "ten", "8"), "Yields must be numbers, like 12.5.")
assert_equal(check_inputs("Test", "0", "8"),
             "Theoretical yield must be greater than 0, and actual yield cannot be negative.")
assert_equal(check_inputs("Test", "10", "8"), "")
 
assert_equal(index(fresh_state()),
             Page(fresh_state(), [
                 Header("Lab Yield Tracker"),
                 "Record your lab experiments, calculate percent yield, and compare your results.",
                 LineBreak(),
                 Button("New Experiment", new_experiment),
                 Button("View History", history),
                 Button("Help", help_page),
             ]))
 
assert_equal(new_experiment(fresh_state()),
             Page(fresh_state(), [
                 Header("New Experiment"),
                 "Experiment name:",
                 TextBox("name"),
                 LineBreak(),
                 "Theoretical yield (grams):",
                 TextBox("theoretical"),
                 LineBreak(),
                 "Actual yield (grams):",
                 TextBox("actual"),
                 LineBreak(),
                 Button("Calculate", save_experiment),
                 Link("Home", index),
             ]))
assert_equal(new_experiment(State([], "Please fill in every box.", 0.0, "All")),
             Page(State([], "Please fill in every box.", 0.0, "All"), [
                 Header("New Experiment"),
                 "Experiment name:",
                 TextBox("name"),
                 LineBreak(),
                 "Theoretical yield (grams):",
                 TextBox("theoretical"),
                 LineBreak(),
                 "Actual yield (grams):",
                 TextBox("actual"),
                 LineBreak(),
                 "Please fill in every box.",
                 LineBreak(),
                 Button("Calculate", save_experiment),
                 Link("Home", index),
             ]))
 
assert_equal(save_experiment(fresh_state(), "Test", "10", "8").state,
             State([Experiment("Test", 10.0, 8.0, 80.0)], "", 80.0, "All"))
assert_equal(save_experiment(fresh_state(), "", "10", "8").state,
             State([], "Please fill in every box.", 0.0, "All"))
assert_equal(save_experiment(fresh_state(), "Test", "ten", "8").state,
             State([], "Yields must be numbers, like 12.5.", 0.0, "All"))
 
assert_equal(result(State([], "", 80.0, "All")),
             Page(State([], "", 80.0, "All"), [
                 Header("Result"),
                 "Percent yield: 80.0%",
                 LineBreak(),
                 "This is a good yield.",
                 LineBreak(),
                 Button("Add Another", new_experiment),
                 Button("History", history),
             ]))
assert_equal(result(State([], "", 125.0, "All")),
             Page(State([], "", 125.0, "All"), [
                 Header("Result"),
                 "Percent yield: 125.0%",
                 LineBreak(),
                 "Warning: a yield over 100% usually means a measurement error, "
                 "or a wet or impure product.",
                 LineBreak(),
                 Button("Add Another", new_experiment),
                 Button("History", history),
             ]))
assert_equal(result(State([], "", 40.0, "All")),
             Page(State([], "", 40.0, "All"), [
                 Header("Result"),
                 "Percent yield: 40.0%",
                 LineBreak(),
                 "This yield is low. Check for lost product or an incomplete reaction.",
                 LineBreak(),
                 Button("Add Another", new_experiment),
                 Button("History", history),
             ]))
 
assert_equal(history(fresh_state()),
             Page(fresh_state(), [
                 Header("History"),
                 "Show:",
                 SelectBox("choice", ["All", "Good", "Low", "Over 100%"], "All"),
                 Button("Apply Filter", apply_filter),
                 HorizontalRule(),
                 "No experiments yet. Add one to get started.",
                 LineBreak(),
                 Link("Home", index),
             ]))
assert_equal(history(sample_state("All")),
             Page(sample_state("All"), [
                 Header("History"),
                 "Show:",
                 SelectBox("choice", ["All", "Good", "Low", "Over 100%"], "All"),
                 Button("Apply Filter", apply_filter),
                 HorizontalRule(),
                 "Test: 80.0% (Good)",
                 Button("Delete", delete_experiment, Argument("position", 0)),
                 LineBreak(),
                 "Average of shown experiments: 80.0%",
                 LineBreak(),
                 Link("Home", index),
             ]))
assert_equal(history(sample_state("Low")),
             Page(sample_state("Low"), [
                 Header("History"),
                 "Show:",
                 SelectBox("choice", ["All", "Good", "Low", "Over 100%"], "Low"),
                 Button("Apply Filter", apply_filter),
                 HorizontalRule(),
                 "No experiments match this filter.",
                 LineBreak(),
                 Link("Home", index),
             ]))
 
assert_equal(apply_filter(fresh_state(), "Good").state,
             State([], "", 0.0, "Good"))
 
assert_equal(delete_experiment(sample_state("All"), 0).state, fresh_state())
assert_equal(delete_experiment(sample_state("All"), 5).state, sample_state("All"))
 
assert_equal(help_page(fresh_state()),
             Page(fresh_state(), [
                 Header("Help"),
                 "Percent yield = actual yield / theoretical yield * 100.",
                 LineBreak(),
                 "Theoretical yield is the most product the reaction could make. "
                 "Actual yield is what you collected.",
                 LineBreak(),
                 "A result over 100% usually means a measurement mistake, "
                 "or a product that was still wet or impure.",
                 LineBreak(),
                 "On the history page, Good means 70% or more, and Low means under 70%.",
                 LineBreak(),
                 Button("Home", index),
             ]))

hide_debug_information()

start_server(State([], "", 0.0, "All"))
