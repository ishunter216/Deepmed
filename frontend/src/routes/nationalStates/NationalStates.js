import React from 'react'
import {connect} from 'react-redux'
import withStyles from 'isomorphic-style-loader/lib/withStyles'
import s from './NationalStates.scss'
import {Col, Row, VectorMap, Spin} from '../../components'
import {Line} from 'react-chartjs-2'
import {humanReadableNumber} from '../../utils'
import cn from 'classnames'
import reduce from 'lodash/reduce'
import assign from 'lodash/assign'
import uniq from 'lodash/uniq'
import sortBy from 'lodash/sortBy'
import isEmpty from 'lodash/isEmpty'

const colors = ['#47cfd1', '#04a9a9', '#48ccf5', '#77c2d9']
const chartColors = ['#88d0d1', '#48ccf5']
const chartLabels = ['Incidence', 'Deaths']

class NationalStates extends React.Component {
  render() {
    const {individualStatistics} = this.props

    let states
    let ranges
    if (individualStatistics.breast_cancer_by_state && individualStatistics.breast_cancer_by_state.length) {
      states = reduce(individualStatistics.breast_cancer_by_state, (acc, {State, Range}) => assign(acc, {[`US-${State}`]: Range}), {})
      ranges = sortBy(uniq(individualStatistics.breast_cancer_by_state.map(item => item.Range)), x => x)
    }

    return (
      <div className='container container-full'>

        <Row type='flex' gutter={16}>
          <Col xs={24} md={12} className={s.col}>
            <div className={cn(s.card, s.mapCard)}>

              <h2 className='text-center'>Breast Cancer Incidence per 100,000 Women</h2>

              <div className={s.mapWrapper}>
                {states ? (
                  <VectorMap
                    map='us_aea'
                    backgroundColor='transparent'
                    series={{
                      regions: [{
                        values: states,
                        scale: colors,
                      }]
                    }}
                    onRegionTipShow={(e, el, code) => {
                      const currentState = individualStatistics.breast_cancer_by_state.find(item => code.includes(item.State)) || {}
                      el.html(el.html() + `<div>Range: ${currentState.Range}<br/>Rate: ${currentState.Rate}</div>`)
                    }}
                    containerStyle={{width: '100%', height: 500}}
                    regionStyle={{
                      initial: {
                        stroke: 'white',
                        'stroke-width': 2,
                        'stroke-opacity': 1,
                      },
                    }}
                  />
                ) : (
                  <Spin spinning/>
                )}
              </div>
              {ranges && (
                <div className={s.rangesCard}>
                  <p className={s.rangesCardHeader}>Range:</p>
                  <Row gutter={4} className={s.rangesCardContent}>
                    {ranges.map((range, i) =>
                      <Col span='6' key={range} className={s.range}>
                        <span className={s.rangeIndicator} style={{backgroundColor: colors[i]}}/>
                        <p className={s.rangeLabel}>{range}</p>
                      </Col>
                    )}
                  </Row>
                </div>
              )}
            </div>
          </Col>

          <Col xs={24} md={12} className={s.col}>
            <div className={s.card}>

              <h2 className='no-margin text-center'>Breast Cancer Incidence over Time</h2>
              <div className='custom-panel custom-panel-condensed push-top-2'>
                <div className='row row-condensed'>
                  <div className='col-sm-12'>
                    <p className='push-top-1 push-bot-2 text-center'>
                      <strong>Number per 100,000 females</strong>
                    </p>
                    {!isEmpty(individualStatistics.breast_cancer_at_a_glance) ? (
                      <Line
                        data={{
                          ...individualStatistics.breast_cancer_at_a_glance,
                          datasets: individualStatistics.breast_cancer_at_a_glance.datasets.map((item, i) => ({
                            ...item,
                            label: [chartLabels[i]],
                            backgroundColor: chartColors[i],
                            borderColor: chartColors[i],
                          }))
                        }}
                        width={500}
                        height={200}
                        options={{
                          legend: {
                            onClick: () => {
                            },
                            position: 'bottom',
                          },
                          scales: {
                            yAxes: [{
                              ticks: {
                                beginAtZero: true,
                              }
                            }]
                          },
                        }}
                      />
                    ) : (
                      <Spin spinning/>
                    )}
                  </div>
                </div>
                <div className='row row-condensed push-top-2'>
                  <div className='col-sm-6'>
                    <div className='custom-panel custom-panel-condensed no border green-bg push-bot-0'>
                      <div className='display-table display-table-100'>
                        <div className='display-table-cell'>
                          <p className='no-margin text-white small'>
                            Estimated New<br/>Cases in 2017
                          </p>
                        </div>
                        <div className='display-table-cell text-right'>
                          <p className='no-margin text-white'>
                            <strong>252,719</strong>
                          </p>
                        </div>
                      </div>
                    </div>
                    <div className='custom-panel custom-panel-condensed no border green-bg push-bot-0'>
                      <div className='display-table display-table-100'>
                        <div className='display-table-cell'>
                          <p className='no-margin text-white small'>
                            % of All New<br/>Cancer Cases
                          </p>
                        </div>
                        <div className='display-table-cell text-right'>
                          <p className='no-margin text-white'>
                            <strong>15.0%</strong>
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className='col-sm-6'>
                    <div className='custom-panel custom-panel-condensed no border blue-bg push-bot-0'>
                      <div className='display-table display-table-100'>
                        <div className='display-table-cell'>
                          <p className='no-margin text-white small'>
                            Estimated<br/>Deaths in 2017
                          </p>
                        </div>
                        <div className='display-table-cell text-right'>
                          <p className='no-margin text-white'>
                            <strong>40,610</strong>
                          </p>
                        </div>
                      </div>
                    </div>
                    <div className='custom-panel custom-panel-condensed no border blue-bg push-bot-0'>
                      <div className='display-table display-table-100'>
                        <div className='display-table-cell'>
                          <p className='no-margin text-white small'>
                            % of All<br/>Cancer Deaths
                          </p>
                        </div>
                        <div className='display-table-cell text-right'>
                          <p className='no-margin text-white'>
                            <strong>6.8%</strong>
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className='custom-panel custom-panel-condensed push-bot-0'>
                <div className='display-table'>
                  <div className='display-table-cell display-block-xs'>
                    <div
                      className='custom-panel custom-panel-condensed gradient-bg text-center push-bot-0'>
                      <p className='no-margin text-white'><strong>5 year survival rate</strong></p>
                      <p className='font-size-40 push-top-1 push-bot-1 text-white'>
                        <strong>89.7%</strong></p>
                      <p className='no-margin text-white text-light'>2017-2013</p>
                    </div>
                  </div>
                  <div className='display-table-cell display-block-xs push-top-2-xs pad-left-1'>
                    <p className='push-bot-1'>
                      Number of New Cases and Deaths per 100,000: The number of new cases of female breast cancer was
                      124.9 per 100,000 women per year. The number of deaths was 21.2 per 100,000 women per year. These
                      rates are age-adjusted and based on 2010-2014 cases and deaths.
                    </p>
                    <p className='push-bot-1'>
                      Lifetime Risk of Developing Cancer: Approximately 12.4 percent of women will be diagnosed with
                      female breast cancer at some point during their lifetime, based on 2012-2014 individualStatistics.
                    </p>
                    <p>
                      Prevalence of Breast Cancer: In 2014, there were an estimated 3,327,552 women living with female
                      breast cancer in the United States.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </Col>
        </Row>

        <div className='custom-panel custom-panel-condensed light-gray-bg'>

          <h2 className='no-margin text-center'>Breast Cancer by Age</h2>

          <Row type='flex' gutter={16}>
            <Col xs={24} md={12}>
              <div className={s.card}>
                <p className='push-top-1 push-bot-2 text-center'><strong>Age-Specific Rates of
                  Breast Cancer in the United States</strong></p>
                {!isEmpty(individualStatistics.breast_cancer_by_age) ? (
                  <Line
                    data={individualStatistics.breast_cancer_by_age}
                    options={{
                      legend: {
                        display: false,
                        position: 'bottom'
                      },
                      scales: {
                        yAxes: [{
                          ticks: {
                            beginAtZero: true,
                            callback: humanReadableNumber
                          }
                        }]
                      },
                    }}
                    width={275}
                    height={100}
                  />
                ) : (
                  <Spin spinning/>
                )}
              </div>
            </Col>
            <Col xs={24} md={12}>
              <div className={s.card}>
                <p className='push-top-1 push-bot-2 text-center'>
                  <strong>Percent of Women who Develop Breast Cancer By Age</strong>
                </p>
                <div className='custom-panel custom-panel-condensed push-bot-0'>
                  <table className='table table-responsive table-middle-cell-align table-hover'>
                    <thead>
                    <tr>
                      <th><h6>CURRENT AGE</h6></th>
                      <th><h6>10 YEARS</h6></th>
                      <th><h6>20 YEARS</h6></th>
                      <th><h6>30 YEARS</h6></th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr>
                      <td><p>30</p></td>
                      <td><p>0.44</p></td>
                      <td><p>1.87</p></td>
                      <td><p>4.05</p></td>
                    </tr>
                    <tr>
                      <td><p>40</p></td>
                      <td><p>1.44</p></td>
                      <td><p>3.65</p></td>
                      <td><p>6.80</p></td>
                    </tr>
                    <tr>
                      <td><p>50</p></td>
                      <td><p>2.28</p></td>
                      <td><p>5.53</p></td>
                      <td><p>8.75</p></td>
                    </tr>
                    <tr>
                      <td><p>60</p></td>
                      <td><p>3.46</p></td>
                      <td><p>6.89</p></td>
                      <td><p>8.89</p></td>
                    </tr>
                    <tr>
                      <td><p>70</p></td>
                      <td><p>3.89</p></td>
                      <td><p>6.16</p></td>
                      <td><p>N/A</p></td>
                    </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </Col>
          </Row>
        </div>
      </div>
    )
  }
}

const mapState = state => ({
  ...state.diagnosis,
})

const mapDispatch = {}

export default connect(mapState, mapDispatch)(withStyles(s)(NationalStates))
