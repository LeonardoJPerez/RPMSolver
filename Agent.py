# Your Agent for solving Raven's Progressive Matrices. You MUST modify this file.
#
# You may also create and submit new files in addition to modifying this file.
#
# Make sure your file retains methods with the signatures:
# def __init__(self)
# def Solve(self,problem)
#
# These methods will be necessary for the project's main method to run.

# Install Pillow and uncomment this line to access image processing.
from collections import OrderedDict
from PIL import Image

import HelperModels as hm
import numpy as np
import uuid
import itertools


class Agent:
    # The default constructor for your Agent. Make sure to execute any
    # processing necessary before your Agent starts solving problems here.
    #
    # Do not add any variables to this signature; they will not be used by
    # main().

    def __init__(self):
        self.FlaggedProps = ["inside", "angle", "above"]
        self.AlignmentMirrors = {
            "bottom-left": "bottom-right",
            "top-left": "top-right",
            "bottom-right": "bottom-left",
            "top-right": "top-left",
            "left": "right",
            "right": "left"
        }

    # The primary method for solving incoming Raven's Progressive Matrices.
    # For each problem, your Agent's Solve() method will be called. At the
    # conclusion of Solve(), your Agent should return an int representing its
    # answer to the question: 1, 2, 3, 4, 5, or 6. Strings of these ints
    # are also the Names of the individual RavensFigures, obtained through
    # RavensFigure.getName(). Return a negative number to skip a problem.
    #
    # Make sure to return your answer *as an integer* at the end of Solve().
    # Returning your answer as a string may cause your program to crash.
    def Solve(self, problem):
        print(problem.name)
        if problem.hasVerbal:
            # Lets use the verbal process. Otherwise let get the image data.
            return self.ProcessVerbal(problem)
        else:
            print("No Verbal representation found.")

        return -1

    def ProcessVerbal(self, problem):
        problemSet = OrderedDict()
        answerSet = OrderedDict()
        potentialAnswers = None

        for key in sorted(problem.figures.keys()):
            if key.isalpha():
                problemSet[key] = problem.figures[key]
            else:
                answerSet[key] = problem.figures[key]

        # Check if problem is 2x2 or 3x3
        if problem.problemType == '2x2':
            potentialAnswers = self.Solve2By2(problemSet, answerSet)
 
        return next(iter(potentialAnswers or []), None)[0]

    # def IterateProps(self, figure):
    #     for key in figure.objects:
    #         obj = figure.objects[key]
    #         for property, value in obj.attributes.items():
    #             print(property, ": ", value)
    #     return -1

    def GenerateSN(self, frame):
        sn = OrderedDict()

        # print("Frame objects count: " + str(len(frame.objects.items())))
        for key in sorted(frame.objects.keys()):
            node = hm.Node()
            node.label = key
            node.props = frame.objects[key].attributes

            # links will be added if frame.object has certain keywords.
            # there keywords will be added to a collection of relationship
            # keywords among frame objects.

            sn[key] = node

        return sn

    def Solve2By2(self, problemSet, answerSet):
        aSn = self.GenerateSN(problemSet['A'])
        bSn = self.GenerateSN(problemSet['B'])

        diffProps = OrderedDict()
        for akey, bkey in zip(aSn, bSn):
            aFigure = aSn[akey]
            bFigure = bSn[bkey]

            controlProps = self.cleanProps(aFigure.props, bFigure.props)
            for ap, bp in controlProps:
                if not ap or not bp:
                    continue

                aPropValue = aFigure.props[ap]
                bPropValue = bFigure.props[bp]
                if (ap == bp) and (aPropValue != bPropValue):
                    # if prop is a flag one (relative to frame one such as
                    # inside, left of, etc. Locate the index of the relative
                    # value.)

                    if bp == 'inside' or bp == 'above':
                        aRelIndex = list(aSn.keys()).index(aPropValue)
                        bRelIndex = list(bSn.keys()).index(bPropValue)

                        if aRelIndex == aRelIndex:
                            continue
                        else:
                            diffProps[bp] = aRelIndex
                    elif bp == 'angle':
                        angleDiff = int(aPropValue) - int(bPropValue)
                        diffProps[bp] = abs(angleDiff)
                    elif bp == 'alignment':
                        # check if change is mirror.
                        if self.AlignmentMirrors[aPropValue] == bPropValue:
                            # Relationship is mirrored.
                            diffProps[bp] = "mirrored"

                    else:
                        diffProps[bp] = bPropValue

        # for each node(figure) in aSn, compare its props and links with bSn.
        # If the prop exist in aSn and bSn AND its value in bSn IS NOT the same
        #       Add the property to a list of transformation changes.
        # This list will used to find the props in C that will be compared to
        # each of the answers.

        # Compare aSn tree with bSn
        # Calculate difference (transformation) between A and B.
        # Changed values of properties, removed values, etc.

        cSn = self.GenerateSN(problemSet['C'])
        answersSn = []
        for key in answerSet:
            answersSn.append(self.GenerateSN(answerSet[key]))

        # Transformation Verification
        validAnswers = []
        for i, answer in enumerate(answersSn):
            pAnswer = 0 #potential Answer
            for ckey, awkey in zip(cSn, answer):
                cFigure = cSn[ckey]
                awFigure = answer[awkey]              

                if not diffProps:
                    # No differences found. Find a frame that matches Frame C in all
                    # props.
                    noDiffs = True
                    mapped = self.cleanProps(cFigure.props, awFigure.props)
                    for cp, awp in mapped:
                        cPropValue = cFigure.props[cp]
                        awPropValue = awFigure.props[awp]

                        # and (awp not in self.FlaggedProps):
                        if (cp == awp) and (cPropValue != awPropValue):
                            # if inside and relative position
                            if cp == 'inside' or cp == 'above':
                                cRelIndex = list(cSn.keys()).index(cPropValue)
                                awRelIndex = list(answer.keys()).index(awPropValue)

                                if cRelIndex == awRelIndex:
                                    continue
                            else:
                                noDiffs = False
                                break

                    if noDiffs:
                        pAnswer += 1

                else:
                    mappedProp = self.cleanProps(cFigure.props, awFigure.props)
                    for cp, awp in mappedProp:
                        if not cp or not awp:
                            continue

                        cPropValue = cFigure.props[cp]
                        awPropValue = awFigure.props[awp]

                        if cp in diffProps and awp in diffProps:
                            if (cp == awp) and (cPropValue != awPropValue):
                                if awp == 'inside' or awp == 'above':
                                    # check to see if position of awp matches stored pos.
                                    cRelIndex = list(cSn.keys()).index(cPropValue)
                                    awRelIndex = list(answer.keys()).index(awPropValue)

                                    if awRelIndex == diffProps[awp]:
                                        pAnswer += 1

                                elif awp == 'angle':
                                    # substract stored angle and match result with awp. if they match add to answers.
                                    angleDiff = int(cPropValue) - int(awPropValue)

                                    if angleDiff == diffProps[awp]:
                                        pAnswer += 1
                                elif awp == 'alignment':
                                    if diffProps[awp] == "mirrored":
                                        # check prop value from awp and see if its truly mirrored.
                                        if self.AlignmentMirrors[cPropValue] == awPropValue:
                                            pAnswer += 1                               
                                else:
                                    pAnswer += 1                   

            validAnswers.append((i + 1, pAnswer, answer))
            
        validAnswers = sorted(validAnswers, key=lambda ans: ans[1], reverse=True) 
        print(str(next(iter(validAnswers or []), None)[0]))

        return validAnswers

    def cleanProps(self, xp, yp):
        newD = []
        dupes = []
        uniques = []

        for ykey in yp:
            if ykey in xp:
                dupes.append(ykey)
            else:
                uniques.append(ykey)

        for xkey in xp:
            if xkey in yp:
                dupes.append(xkey)
            else:
                uniques.append(xkey)

        dupes = sorted(list(set(dupes)))
        dupesPlusUniques = list(sorted(set(dupes)) + sorted(set(uniques)))

        return itertools.zip_longest(dupes, dupesPlusUniques) 
