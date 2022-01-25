#!/bin/env python3
from email.policy import default
import sys
import xml.etree.ElementTree as ET
import argparse
import graphviz
import re
import hashlib

colors = [
    'aquamarine',
    'burlywood',
    'coral',
    'cyan',
    'lightsteelblue',
    'yellow',
    'magenta',
    'navajowhite',
    'red',
#    'royalblue',
    'wheat',
#    'whitesmoke',
];

def main():
    parser = argparse.ArgumentParser(description='Create diagrams from BPMN files')
    parser.add_argument('--input', type=argparse.FileType('r'), default=sys.stdin, help='the input BPMN file')
    parser.add_argument('--output', type=argparse.FileType('w'), default=sys.stdout, help='the ouput DOT file')
    parser.add_argument('--service-task-regexp', type=str, default=r'\$\{environment\.services\.(.*)\}', help='extract the relevant part from service task implementations')
    parser.add_argument('--condition-regexp', type=str, default=r'next\(null,(.*)\)', help='extract the relevant part from conditions')
    parser.add_argument('--service-task-font-name', type=str, default='Courier')
    parser.add_argument('--sequence-font-name', type=str, default='Courier')
    parser.add_argument('--wait-task-font-name', type=str, default='Arial')


    args = parser.parse_args()

    bpmn = ET.parse(args.input)
    dot = get_dot(bpmn, args)
    args.output.write(dot.source)

def get_dot(bpmn, args):
    remaining_colors = colors[:]
    assigned_colors = {}

    graph = graphviz.graphs.Digraph()
    graph.graph_attr['splines'] = 'ortho'
    graph.graph_attr['overlap_scaling'] = '10000'
    graph.graph_attr['overlap'] = 'scalexy'
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

            graph.edge(element.attrib['sourceRef'], element.attrib['targetRef'], xlabel=label, fontname=args.sequence_font_name)
        elif element.tag.endswith('serviceTask'):
            implementation = element.attrib['implementation']
            match = re.match(args.service_task_regexp, implementation)
            (label,) = match and match.groups() or (implementation,)
            (action, ) = re.match('^([a-zA-Z]+)', label).groups()
            color = assigned_colors.get(action)
            if not color:
                i = hashlib.md5(action.encode('utf-8')).digest()[-1] % len(remaining_colors)
                color = remaining_colors.pop(i)
                assigned_colors[action] = color
            graph.node(element.attrib['id'], label=label, shape='box', fontname=args.service_task_font_name, style='filled', fillcolor=color)
        elif element.tag.endswith('userTask'):
            graph.node(element.attrib['id'], label='User Task', fontname=args.wait_task_font_name)
        elif element.tag.endswith('receiveTask'):
            graph.node(element.attrib['id'], label='Receive Task', fontname=args.wait_task_font_name)
        elif element.tag.endswith('Event'):
            graph.node(element.attrib['id'], fontname=args.wait_task_font_name)

    return graph

if __name__ == '__main__':
    main()