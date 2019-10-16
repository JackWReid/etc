import React, { Component } from 'react';

import SiteHeader from './components/SiteHeader';

import PeopleSection from './sections/People';
import PaymentsSection from './sections/Payments';
import BillsSection from './sections/Bills';
import FooterSection from './sections/Footer';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = props.appState;
  }

  addPeopleRow = () => this.setState(old => {
    old.people.push({name: '', salary: 0})
    return { people: old.people };
  });

  deletePeopleRow = index => this.setState(old => {
    old.people.splice(index, 1);
    return { people: old.people };
  });

  addPaymentRow = () => this.setState(old => {
    old.payments.push({name: '', amount: 0})
    return { payments: old.payments };
  });

  deletePaymentRow = index => this.setState(old => {
    old.payments.splice(index, 1);
    return { payments: old.payments };
  });

  handlePeopleChange = (index, field, value) => {
    this.setState(old => {
      const { people } = old;
      people[index][field] = value;
      return { people };
    });
  }

  handlePaymentChange = (index, field, value) => {
    this.setState(old => {
      const { payments } = old;
      payments[index][field] = value;
      return { payments };
    });
  }

  render() {
    const { people, payments } = this.state;
    const { updateQueryState } = this.props;

    updateQueryState(this.state);

    return (
      <div>
        <SiteHeader />
        <PeopleSection
          addRow={this.addPeopleRow}
          deleteRow={this.deletePeopleRow}
          handleChange={this.handlePeopleChange}
          people={people} />
        <PaymentsSection
          addRow={this.addPaymentRow}
          deleteRow={this.deletePaymentRow}
          handleChange={this.handlePaymentChange}
          payments={payments} />
        <BillsSection
          people={people}
          payments={payments} />
        <FooterSection />
      </div>
    );
  }
}

export default App;
