import React from 'react';
import { css } from 'glamor';

import Section from '../components/Section';

const getRatio = people => {
  const salaryUnit = 1 / people.map(person => person.salary).reduce((acc, val) => acc + val, 0);
  return people.map(person => ({
    ratio: salaryUnit * person.salary,
    ...person,
  }));
};

const getTotals = (people, payments) => {
  const ratios = getRatio(people).map(person => person.ratio);
  const totals = people.map((person, index) =>
  payments.map(payment => payment.amount).reduce((acc, val) => acc + val, 0) * ratios[index]);
  return totals;
}

const thStyle = {
  padding: 4,
  fontWeight: 'normal',
  '@media print': {fontWeight: 'bold'},
};

const tdStyle = {
  padding: 4,
};

export default ({people, payments}) => {
  if (people.length < 1 || payments.length < 1) {
    return null;
  }

  if (people.length === 1 && people[0].salary === 0) {
    return null;
  }

  return (
    <Section>
      <h1>The Bill</h1>
      <p>Here’s who pays what, based on how much everybody can afford.</p>
      <table
        {...css({
        width: '100%',
        border: 'none',
        })}
        cellSpacing="0"
        cellPadding="0"
      >
        <thead {...css({
          textAlign: 'left',
          color: '#777',
        })}>
          <tr>
            <th {...css(thStyle)}>Payment</th>
            {people.map((people, index) =>
              <th {...css(thStyle)} key={index}>{people.name}</th>)}
            <th {...css(thStyle)}>Total</th>
          </tr>
        </thead>
        <tbody>
          {payments.map((payment, index) => (
            <tr
              key={index}
              {...css({
                ':nth-child(2n)': {
                  backgroundColor: '#EEE',
                }
              })}>
              <td {...css(tdStyle)}>{payment.name.length > 0 ? payment.name : 'Unnamed Bill'}</td>
              {getRatio(people).map((person, index) =>
                <td {...css(tdStyle)} key={index}>£{(payment.amount * person.ratio).toFixed(2)}</td>)}
              <td {...css(tdStyle)}>£{payment.amount}</td>
            </tr>
          ))}
          <tr>
            <td {...css({...tdStyle, fontWeight: 'bold'})}>Total</td>
            {getTotals(people, payments).map((total, index) => (
              <td {...css(tdStyle)} key={index}>£{total.toFixed(2)}</td>
            ))}
            <td />
          </tr>
        </tbody>
      </table>
    </Section>
  );
}
