import React, { Component } from 'react';
import { css } from 'glamor';

import Section from '../components/Section';
import Label from '../components/Label';
import TextInput from '../components/TextInput';
import IconAdd from '../components/IconAdd';
import IconRemove from '../components/IconRemove';

const iconButton = {
  display: 'flex',
  alignItems: 'center',
  appearance: 'none',
  padding: 0,
  fontSize: 14,
  fontFamily: 'Helvetica, Arial, sans-serif',
  border: 'none',
  background: 'none',
  cursor: 'pointer',
  '& > img': {
    marginRight: 8,
  }
};

const sanitizeNumericalInput = input => {
  if (input === '') { return 0; }
  return parseFloat(input);
}

export default class People extends Component {
  render() {
    const { people, handleChange, addRow, deleteRow } = this.props;

    return (
      <Section {...css({'@media print': {display: 'none'}})}>
        <h1>People</h1>
        <p>Who are you splitting the bills between and how much do they make a year?</p>
        <div {...css({display: 'flex', marginBottom: 8})}>
          <Label {...css({width: '50%', marginRight: 16})}>Name</Label>
          <Label {...css({width: '50%', marginRight: 16})}>Salary</Label>
          {people.length > 1 && <div {...css({width: 24, height: 24})} />}
        </div>
        {people.map((person, index) => (
          <div
            key={index}
            {...css({
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              marginBottom: 16,
            })}>
            <TextInput
              {...css({width: '50%', marginRight: 16})}
                name={`person-name-${index}`}
                onChange={event => handleChange(index, 'name', event.target.value)}
                value={person.name}
                placeholder="Joe Bloggs" />
            <TextInput
              {...css({width: '50%', marginRight: 16})}
              name={`person-salary-${index}`}
              onChange={event => handleChange(index, 'salary', sanitizeNumericalInput(event.target.value))}
              type="number"
              min="0"
              step="100"
              value={person.salary}
              placeholder="20000" />
            {people.length > 1 && <button
              {...css(iconButton)}
              onClick={() => deleteRow(index)}>
              <IconRemove />
            </button>}
          </div>
        ))}
        <button
          {...css(iconButton)}
          onClick={addRow}>
          <IconAdd />
          <span>Add another person</span>
        </button>
      </Section>
    );
  }
}
