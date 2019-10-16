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

export default class Payments extends Component {
  render() {
    const { payments, handleChange, addRow, deleteRow } = this.props;

    return (
      <Section {...css({'@media print': {display: 'none'}})}>
        <h1>Payments</h1>
        <p>What payments are you splitting? Please express the amount in monthly costs.</p>
        <div {...css({display: 'flex', marginBottom: 8})}>
          <Label {...css({width: '50%', marginRight: 16})}>Name</Label>
          <Label {...css({width: '50%', marginRight: 16})}>Amount</Label>
          {payments.length > 1 && <div {...css({width: 24, height: 24})} />}
        </div>
        {payments.map((payment, index) => (
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
                name={`payment-name-${index}`}
                onChange={event => handleChange(index, 'name', event.target.value)}
                value={payment.name}
                placeholder="Water" />
            <TextInput
              {...css({width: '50%', marginRight: 16})}
              name={`payment-amount-${index}`}
              onChange={event => handleChange(index, 'amount', sanitizeNumericalInput(event.target.value))}
              type="number"
              min="0"
              step="1"
              value={payment.amount}
              placeholder="30" />
            {payments.length > 1 && <button
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
          <span>Add another payment</span>
        </button>
      </Section>
    );
  }
}
