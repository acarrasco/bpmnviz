#!/bin/env python3
from email.policy import default
import sys
import xml.etree.ElementTree as ET
import argparse
import graphviz
import re

def main():
    parser = argparse.ArgumentParser(description='Create diagrams from BPMN files')
    parser.add_argument('--input', type=argparse.FileType('r'), default=sys.stdin, help='the input BPMN file')
    parser.add_argument('--output', type=argparse.FileType('w'), default=sys.stdout, help='the ouput DOT file')
    parser.add_argument('--service-task-regexp', type=str, default=r'\$\{environment\.services\.(.*)\}', help='extract the relevant part from service task implementations')
    parser.add_argument('--condition-regexp', type=str, default=r'next\(null,(.*)\)', help='extract the relevant part from conditions')
    parser.add_argument('--font-name', type=str, default='Ubuntu Mono')

    args = parser.parse_args()

    bpmn = ET.parse(args.input)
    dot = get_dot(bpmn, args)
    args.output.write(dot.source)

def get_dot(bpmn, args):
    graph = graphviz.graphs.Digraph()
    graph.graph_attr['splines'] = 'ortho'
    #graph.graph_attr['overlap'] = 'prism'
    graph.graph_attr['overlap_scaling'] = '10000'
    graph.graph_attr['overlap'] = 'scalexy'
    graph.graph_attr['fontname'] = args.font_name
    is_default_branch = set()
    for element in bpmn.iter():
        if element.tag.endswith('Task'):
            default = element.attrib.get('default')
            if default:
                is_default_branch.add(default)

    for element in bpmn.iter():
        if element.tag.endswith('sequenceFlow'):
            condition = next((x for x in element.iter() if x.tag.endswith('conditionExpression')), None)
            text = condition is not None and condition.text
            if text:
                match = re.match(args.condition_regexp, text)
                (label,) = match and match.groups() or (text,)
            else:
                label = element.attrib['id'] in is_default_branch and 'default' or ''

            graph.edge(element.attrib['sourceRef'], element.attrib['targetRef'], xlabel=label)
        elif element.tag.endswith('serviceTask'):
            implementation = element.attrib['implementation']
            match = re.match(args.service_task_regexp, implementation)
            (label,) = match and match.groups() or (implementation,)
            graph.node(element.attrib['id'], label=label, shape='box')
        elif element.tag.endswith('userTask'):
            graph.node(element.attrib['id'], label='User Task')
        elif element.tag.endswith('receiveTask'):
            graph.node(element.attrib['id'], label='Receive Task')

    return graph

if __name__ == '__main__':
    main()