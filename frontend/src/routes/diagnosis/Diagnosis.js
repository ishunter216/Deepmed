import React from 'react'
import {connect} from 'react-redux'
import withStyles from 'isomorphic-style-loader/lib/withStyles'
import s from './Diagnosis.scss'
import {RACES, REGIONS, SITES, TYPES} from '../../constants'
import {createForm} from 'rc-form'
import messages from '../../components/messages'
import {Input, InputNumber, Select, Spin} from '../../components'
import isEmpty from 'lodash/isEmpty'
import {getData} from '../../reducers/diagnosis'
import cn from 'classnames'
import isNil from 'lodash/isNil'
import {Tab, Tabs} from 'react-bootstrap'

const OverallPlansTable = ({items = [], visibleRowIndex}) =>
  <div className='table-responsive'>
    <table className={cn('table', s.overallPlansTable)}>
      <thead>
      <tr className={s.overallPlansTopHeader}>
        <th colSpan={3}><h6>SURGERY</h6></th>
        <th colSpan={2}><h6>RADIATION</h6></th>
        <th colSpan={2}><h6>CHEMOTHERAPY</h6></th>
      </tr>
      <tr className={s.overallPlansBottomHeader}>
        <th><h6>RECOMMENDATION</h6></th>
        <th><h6>TYPE</h6></th>
        <th className={s.borderRight}><h6>CONFIDENCE</h6></th>
        <th><h6>RECOMMENDATION</h6></th>
        <th className={s.borderRight}><h6>CONFIDENCE</h6></th>
        <th><h6>RECOMMENDATION</h6></th>
        <th><h6>CONFIDENCE</h6></th>
      </tr>
      </thead>
      <tbody>
      {items[visibleRowIndex] ? (
        <tr>
          <td>{items[visibleRowIndex].surgery}</td>
          <td>{items[visibleRowIndex].type}</td>
          <td
            className={s.borderRight}>{items[visibleRowIndex].surgery_confidence_level}{items[visibleRowIndex].type === 'N/A' ? '' : '%'} </td>
          <td>{items[visibleRowIndex].radiation}</td>
          <td className={s.borderRight}>{items[visibleRowIndex].radiation_confidence_level}%</td>
          <td>{items[visibleRowIndex].chemo}</td>
          <td>{items[visibleRowIndex].chemo_confidence_level}%</td>
        </tr>
      ) : (
        <tr>
          <td colSpan={7} style={{textAlign: 'center'}}>N/A</td>
        </tr>
      )}
      </tbody>
    </table>
  </div>

class Diagnosis extends React.Component {
  state = {
    tab: 0,
  }

  handleSubmit = (e) => {
    e.preventDefault()
    this.props.form.validateFields((err, values) => {
      if (!err) {
        this.props.getData(values)
      }
    })
  }

  changeTab = (tab) => {
    this.setState({tab})
  }

  render() {
    const {tab} = this.state
    const {diagnosis, diagnosisForm} = this.props
    const {getFieldDecorator, getFieldError} = this.props.form

    let showRadiation = false

    if (diagnosis.overall_plans && diagnosis.overall_plans[tab] && diagnosis.overall_plans[tab].radiation === 'Yes') {
      showRadiation = true
    }

    return (
      <div className='container container-full'>
        <div className='row'>
          <div className='col-md-12'>
            {!isEmpty(diagnosisForm) && (
              <div className='custom-panel custom-panel-condensed light-gray-bg'>
                <h2 className='push-top-2'>Diagnosis</h2>
                <form onSubmit={this.handleSubmit}>
                  <div className={s.row}>
                    <div className={s.col}>
                      {getFieldDecorator('age', {
                        initialValue: diagnosisForm.age,
                        rules: [
                          {required: true, message: messages.required},
                          {min: 18, message: messages.minAge, type: 'number'},
                        ]
                      })(
                        <InputNumber error={getFieldError('age')} label={'Age at Diagnosis'}/>
                      )}
                    </div>
                    <div className={s.col}>
                      {getFieldDecorator('tumor_size_in_mm', {
                        initialValue: diagnosisForm.tumor_size_in_mm,
                        rules: [
                          {required: true, message: messages.required},
                        ]
                      })(
                        <Input error={getFieldError('tumor_size_in_mm')} label={'Tumor Size in mm'}/>
                      )}
                    </div>
                    <div className={s.col}>
                      {getFieldDecorator('tumor_grade', {
                        initialValue: diagnosisForm.tumor_grade,
                        rules: [
                          {required: true, message: messages.required},
                        ]
                      })(
                        <Select error={getFieldError('tumor_grade')} label={'Tumor Grade'}>
                          <option value='' disabled hidden>Select...</option>
                          <option value={1}>1 (Low)</option>
                          <option value={2}>2 (Medium)</option>
                          <option value={3}>3 (High)</option>
                        </Select>
                      )}
                    </div>
                    <div className={s.col}>
                      {getFieldDecorator('num_pos_nodes', {
                        initialValue: diagnosisForm.num_pos_nodes,
                        rules: [
                          {required: true, message: messages.required},
                        ]
                      })(
                        <Select error={getFieldError('num_pos_nodes')} label={'Number of Positive Nodes'}>
                          <option value='' disabled hidden>Select...</option>
                          {Array.from(new Array(24), (val, i) =>
                            <option key={i} value={i}>{i === 23 ? i + '+' : i}</option>
                          )}
                        </Select>
                      )}
                    </div>
                    <div className={s.col}>
                      {getFieldDecorator('er_status', {
                        initialValue: diagnosisForm.er_status,
                        rules: [
                          {required: true, message: messages.required},
                        ]
                      })(
                        <Select error={getFieldError('er_status')} label={'ER Status'}>
                          <option value='' disabled hidden>Select...</option>
                          <option value='+'>Positive</option>
                          <option value='-'>Negative</option>
                        </Select>
                      )}
                    </div>
                    <div className={s.col}>
                      {getFieldDecorator('pr_status', {
                        initialValue: diagnosisForm.pr_status,
                        rules: [
                          {required: true, message: messages.required},
                        ]
                      })(
                        <Select error={getFieldError('pr_status')} label={'PR Status'}>
                          <option value='' disabled hidden>Select...</option>
                          <option value='+'>Positive</option>
                          <option value='-'>Negative</option>
                        </Select>
                      )}
                    </div>
                    <div className={s.col}>
                      {getFieldDecorator('her2_status', {
                        initialValue: diagnosisForm.her2_status,
                        rules: [
                          {required: true, message: messages.required},
                        ]
                      })(
                        <Select error={getFieldError('her2_status')} label={'HER2 Status'}>
                          <option value='' disabled hidden>Select...</option>
                          <option value='+'>Positive</option>
                          <option value='-'>Negative</option>
                        </Select>
                      )}
                    </div>
                    <div className={s.col}>
                      {getFieldDecorator('ethnicity', {
                        initialValue: diagnosisForm.ethnicity,
                        rules: [
                          {required: true, message: messages.required},
                        ]
                      })(
                        <Select error={getFieldError('ethnicity')} label={'Ethnicity'}>
                          <option value='' disabled hidden>Select...</option>
                          {RACES.map((item, i) =>
                            <option key={i}>{item}</option>
                          )}
                        </Select>
                      )}
                    </div>
                    <div className={s.col}>
                      {getFieldDecorator('region', {
                        initialValue: diagnosisForm.region,
                        rules: [
                          {required: true, message: messages.required},
                        ]
                      })(
                        <Select error={getFieldError('region')} label={'Region'}>
                          <option value='' disabled hidden>Select...</option>
                          {REGIONS.map((item, i) =>
                            <option key={i} value={item.value}>{item.label}</option>
                          )}
                        </Select>
                      )}
                    </div>
                    <div className={s.col}>
                      {getFieldDecorator('laterality', {
                        initialValue: diagnosisForm.laterality,
                        rules: [
                          {required: true, message: messages.required},
                        ]
                      })(
                        <Select error={getFieldError('laterality')} label={'Laterality'}>
                          <option value='' disabled hidden>Select...</option>
                          <option value='left'>Left</option>
                          <option value='right'>Right</option>
                        </Select>
                      )}
                    </div>
                    <div className={s.col}>
                      {getFieldDecorator('site', {
                        initialValue: diagnosisForm.site,
                        rules: [
                          {required: true, message: messages.required},
                        ]
                      })(
                        <Select error={getFieldError('site')} label={'Site'}>
                          <option value='' disabled hidden>Select...</option>
                          {SITES.map((site, i) =>
                            <option key={i} value={site.value}>{site.label}</option>
                          )}
                        </Select>
                      )}
                    </div>
                    <div className={s.col}>
                      {getFieldDecorator('type', {
                        initialValue: diagnosisForm.type,
                        rules: [
                          {required: true, message: messages.required},
                        ]
                      })(
                        <Select error={getFieldError('type')} label={'Type'}>
                          <option value='' disabled hidden>Select...</option>
                          {TYPES.map((item, i) =>
                            <option key={i} value={item.value}>{item.label}</option>
                          )}
                        </Select>
                      )}
                    </div>
                    <div className={s.col}>
                      {getFieldDecorator('number_of_tumors', {
                        initialValue: diagnosisForm.number_of_tumors,
                        rules: [
                          {required: true, message: messages.required},
                        ]
                      })(
                        <Select error={getFieldError('number_of_tumors')} label={'Number of tumors'}>
                          <option value='' disabled hidden>Select...</option>
                          {Array.from(new Array(8), (val, i) =>
                            <option key={i} value={i}>{i}</option>
                          )}
                        </Select>
                      )}
                    </div>
                    <div className={s.col}/>
                  </div>
                  <div className={s.row}>
                    <div className="col-xs-12 text-center position-relative">
                      <button type="submit" className={cn('btn btn-primary', s.analyzeBtn)}>
                        Analyze
                      </button>
                    </div>
                  </div>
                </form>
              </div>
            )}
            <div className={s.card}>
              <h2 className={s.cardHeader}>Recommended Treatment Plans</h2>
              <section className={s.section}>
                <header className={s.sectionHeader}>
                  Overall Plans
                </header>
                <div className={s.sectionContent}>
                  <Tabs
                    activeKey={tab}
                    onSelect={this.changeTab}
                    id='overallPlansTabs'
                    justified
                    animation={false}
                    className={s.overallPlansTabs}
                  >
                    <Tab eventKey={0} title='PREFERRED RECOMMENDATION'>
                      <OverallPlansTable items={diagnosis.overall_plans} visibleRowIndex={0}/>
                    </Tab>
                    <Tab eventKey={1} title='ALTERNATIVE RECOMMENDATION'>
                      <OverallPlansTable items={diagnosis.overall_plans} visibleRowIndex={1}/>
                    </Tab>
                  </Tabs>
                  {isNil(diagnosis.overall_plans) && <Spin spinning/>}
                </div>
              </section>
              <div className='push-top-5'>
                <div
                  className='custom-panel custom-panel-condensed custom-panel-no-vertical-pad no-border bg-transparent push-bot-0'>
                  <p className='push-top-0 push-bot-1'><strong>Chemotherapy</strong></p>
                </div>
                <div className='custom-panel custom-panel-condensed push-bot-0'>
                  <table
                    className='table table-responsive table-middle-cell-align table-equal-width-3 table-hover tablesaw tablesaw-stack'
                    data-tablesaw-mode='stack'>
                    <thead>
                    <tr>
                      <th><h6>TREATMENT PLANS</h6></th>
                      <th><h6>NUMBER OF TREATMENTS</h6></th>
                      <th><h6>ADMINISTRATION</h6></th>
                    </tr>
                    </thead>
                    <tbody>
                    {!isEmpty(diagnosis.chemo_therapy) ? diagnosis.chemo_therapy.map((item, i) =>
                      <tr key={i}>
                        <td><p className='no-margin'><span
                          className='number-circle blue-circle'>{i + 1}</span> {item.plan}</p></td>
                        <td>
                          <table>
                            <tbody>
                            {item.number_of_treatments.map(n =>
                              <tr key={n.name}>
                                <td>
                                  <p className='push-bot-1 push-top-1'>{n.name} {n.value}</p>
                                </td>
                              </tr>
                            )}
                            </tbody>
                          </table>
                        </td>
                        <td>
                          <table>
                            <tbody>
                            {item.administration.map(m =>
                              <tr key={m.name}>
                                <td>
                                  <p className='no-margin'>{m.name}</p>
                                </td>
                                {m.values.map((value, j) =>
                                  <React.Fragment key={j}>
                                    <td className='pad-left-1 pad-right-1'>
                                      <p className='no-margin'>{value.name}</p>
                                      <p className='push-bot-1 line-height-condensed small'>
                                        <small>{value.time}</small>
                                      </p>
                                    </td>
                                    {(j !== m.values.length - 1) && <td className='vertical-line'/>}
                                  </React.Fragment>
                                )}
                              </tr>
                            )}
                            </tbody>
                          </table>
                        </td>
                      </tr>
                    ) : !isNil(diagnosis.chemo_therapy) && (
                      <tr>
                        <td colSpan={3} style={{textAlign: 'center'}}>N/A</td>
                      </tr>
                    )}
                    </tbody>
                  </table>
                  {isNil(diagnosis.chemo_therapy) && <Spin spinning/>}
                </div>
              </div>
              <div className='push-top-5'>
                <div
                  className='custom-panel custom-panel-condensed custom-panel-no-vertical-pad no-border bg-transparent push-bot-0'>
                  <p className='push-top-0 push-bot-1'><strong>Radiation Therapy</strong></p>
                </div>
                <div className='custom-panel custom-panel-condensed push-bot-0'>
                  <table
                    className='table table-responsive table-middle-cell-align table-equal-width-3 table-hover tablesaw tablesaw-stack'
                    data-tablesaw-mode='stack'>
                    <thead>
                    <tr>
                      <th><h6>TREATMENT PLANS</h6></th>
                      <th><h6>NUMBER OF TREATMENTS</h6></th>
                      <th><h6>ADMINISTRATION</h6></th>
                    </tr>
                    </thead>
                    <tbody>
                    {showRadiation && !isEmpty(diagnosis.radiation_therapy) ? diagnosis.radiation_therapy.map((item, i) =>
                      <tr key={i}>
                        <td><p className='no-margin'><span
                          className='number-circle blue-circle'>{i + 1}</span> {item.name}</p></td>
                        <td><p className="no-margin">{item.number_of_treatments}</p></td>
                        <td><p className="no-margin">{item.administration}</p></td>
                      </tr>
                    ) : !isNil(diagnosis.radiation_therapy) && (
                      <tr>
                        <td colSpan={3} style={{textAlign: 'center'}}>N/A</td>
                      </tr>
                    )}
                    </tbody>
                  </table>
                  {isNil(diagnosis.radiation_therapy) && <Spin spinning/>}
                </div>
              </div>
              <div className='push-top-5'>
                <div
                  className='custom-panel custom-panel-condensed custom-panel-no-vertical-pad no-border bg-transparent push-bot-0'>
                  <p className='push-top-0 push-bot-1'><strong>Hormonal Therapy</strong></p>
                </div>
                <div className='custom-panel custom-panel-condensed push-bot-0'>
                  <table
                    className='table table-responsive table-middle-cell-align table-equal-width-3 table-hover tablesaw tablesaw-stack'
                    data-tablesaw-mode='stack'>
                    <thead>
                    <tr>
                      <th><h6>TREATMENT PLANS</h6></th>
                      <th><h6>NUMBER OF TREATMENTS</h6></th>
                      <th><h6>ADMINISTRATION</h6></th>
                    </tr>
                    </thead>
                    <tbody>
                    {!isEmpty(diagnosis.hormonal_therapy) ? diagnosis.hormonal_therapy.map((item, i) =>
                      <tr key={i}>
                        <td><p className='no-margin'><span
                          className='number-circle blue-circle'>{i + 1}</span> {item.name}</p></td>
                        <td><p className="no-margin">{item.number_of_treatments}</p></td>
                        <td><p className="no-margin">{item.administration}</p></td>
                      </tr>
                    ) : !isNil(diagnosis.hormonal_therapy) && (
                      <tr>
                        <td colSpan={3} style={{textAlign: 'center'}}>N/A</td>
                      </tr>
                    )}
                    </tbody>
                  </table>
                  {isNil(diagnosis.hormonal_therapy) && <Spin spinning/>}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }
}

const mapState = state => ({
  ...state.diagnosis,
})

const mapDispatch = {
  getData,
}

export default connect(mapState, mapDispatch)(createForm()(withStyles(s)(Diagnosis)))
