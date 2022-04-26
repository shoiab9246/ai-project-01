#!/usr/local/bin/python3
# assign.py : Assign people to teams
#
# Code by: name IU ID
#
# Based on skeleton code by R. Shah and D. Crandall, January 2021
#

import sys
import time
import itertools
import copy

def solver(input_file):
    """
    1. This function should take the name of a .txt input file in the format indicated in the assignment.
    2. It should return a dictionary with the following keys:
        - "assigned-groups" : a list of groups assigned by the program, each consisting of usernames separated by hyphens
        - "total-cost" : total cost (number of complaints) in the group assignment
    3. Do not add any extra parameters to the solver() function, or it will break our grading and testing code.
    4. Please do not use any global variables, as it may cause the testing code to fail.
    5. To handle the fact that some problems may take longer than others, and you don't know ahead of time how
       much time it will take to find the best solution, you can compute a series of solutions and then
       call "yield" to return that preliminary solution. Your program can continue yielding multiple times;
       our test program will take the last answer you 'yielded' once time expired.
    """
    members = Generate_TeamMembers(input_file)
    Update_Team_Members(members)
    initial_cost = sum([member.get_complaints() for member in members])
    assignment = Assignment([[member] for member in members],initial_cost)
    best_assignment = []
    fringe = [assignment]
    visited = []
    while fringe:
        current = fringe.pop(fringe.index(min(fringe, key=lambda t:t.cost)))
        fringe.extend(Generate_Assignment(current.teams))
        # fringe.sort(key=lambda t: t.cost)

        if len(best_assignment) > 0 and current.cost <= best_assignment[0]["total-cost"]:
            best_assignment.insert(0,Output_Assignment(current))
        else:
            best_assignment.append(Output_Assignment(current))

        yield (best_assignment[0])

    # Simple example. First we yield a quick solution
    # assignment, cost = Generate_Assignment(members)

    #
    #
    # # Then we think a while and return another solution:
    # time.sleep(10)
    # yield(best_assignment[0])
    #
    # time.sleep(10)
    # yield (best_assignment[0])
    # # This solution will never befound, but that's ok; program will be killed eventually by the
    # #  test script.
    # while True:
    #     pass
    #
    # yield({"assigned-groups": ["vibvats-djcran", "zkachwal-shah12-vrmath"],
    #            "total-cost" : 9})


def Generate_TeamMembers(input_file):
    f = open(input_file)
    team_members = []
    for i in f.read().splitlines():
        team_members.append(team_member(i.split(' ')[0], i.split(' ')[1] + ' ' + i.split(' ')[2]))
    return team_members


def Output_Assignment(assignment):
    assigned_groups = []
    for team in assignment.teams:
        team_name = "-".join([member.name for member in team])
        assigned_groups.append(team_name)
    return {'assigned-groups':assigned_groups, 'total-cost':assignment.cost}


def Update_Team_Members(members):
    for member in members:
        add_to_desiredteam(member, members,member.initial_answer.split(' ')[0])
        add_to_missing(member,member.initial_answer.split(' ')[0])
        add_to_undesiredmembers(member, members, member.initial_answer.split(' ')[1])
        member.team_size = len(member.desired_team) + member.missing_members


def add_to_desiredteam(member, members,desired_members_string):
    names = desired_members_string.split('-')
    for name in names:
        if name == member.name:
            continue
        else:
            member.desired_team.extend([teammate for teammate in members if teammate.name == name])


def add_to_missing(member, missing_members):
    names = missing_members.split('-')
    for i in names:
        if i =='zzz':
            member.missing_members += 1


def add_to_undesiredmembers(member, members,desired_members_string):
    names = desired_members_string.split(',')
    for name in names:
        member.undesired_members.extend([teammate for teammate in members if teammate.name == name])


def Generate_Assignment(teams):
    assignments = []
    for i in range(len(teams)):
        for j in range(i+1, len(teams)):
            if len(teams[i]) == 3 or len(teams[j]) == 3 or len(teams[i])+len(teams[j]) > 3:
                continue
            cost = 0
            newlist = copy.deepcopy(teams)
            team1_copy = newlist[i]
            team2_copy = newlist[j]
            if set(teams[i]) == set(teams[j]):
                continue
            else:
                newlist.remove(team1_copy)
                newlist.remove(team2_copy)

                for members1 in team1_copy:
                    for members2 in team2_copy:
                        members1.actual_team.append(members2.name)
                        members2.actual_team.append(members1.name)
                team1_copy.extend(team2_copy)
                newlist.append(team1_copy)
                for team in newlist:
                    cost += sum([member.get_complaints() for member in team])
                assignments.append(Assignment(newlist, cost))
    return assignments


class Assignment:
    def __init__(self, teams, cost):
        self.cost = cost
        self.teams = teams


class team_member:
    def __init__(self, name, answer):
        self.name = name
        self.desired_team = []
        self.undesired_members = []
        self.team_size = 1
        self.actual_team = []
        self.missing_members = 0
        self.initial_answer = answer

    def get_complaints(self):
        complaints = 0
        if len(self.actual_team) != self.team_size:
            complaints += 1
        for members1 in self.undesired_members:
            for members2 in self.actual_team:
                if members1.name == members2:
                    complaints += 2
        for members1 in self.desired_team:
            found = False
            for members2 in self.actual_team:
                if members1.name == members2:
                    found = True
                    break
            if found == False:
                complaints += 1
        return complaints




if __name__ == "__main__":
    if(len(sys.argv) != 2):
        raise(Exception("Error: expected an input filename"))

    for result in solver(sys.argv[1]):
        print("----- Latest solution:\n" + "\n".join(result["assigned-groups"]))
        print("\nAssignment cost: %d \n" % result["total-cost"])
    
