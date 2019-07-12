import React from 'react'
import {connect} from 'react-redux'
import withStyles from 'isomorphic-style-loader/lib/withStyles'
import s from './SimilarDiagnoses.scss'
import {Spin} from '../../components'
import isNil from 'lodash/isNil'

class SimilarDiagnoses extends React.Component {
  render() {
    const {similarDiagnoses} = this.props
    return (
      <div className="container container-full" data-children="same-height">
        <div className="row">
          <div className="col-md-12">
            <div className="custom-panel custom-panel-condensed push-bot-0">
              <div className="table-responsive">
                <table className="table table-middle-cell-align table-hover">
                  <thead>
                  <tr>
                    <th colSpan={11} className={s.borderRight}>
                      <h5 className="text-center">Diagnosis</h5>
                    </th>
                    <th colSpan={3} className={s.borderRight}>
                      <h5 className="text-center">Treatment</h5>
                    </th>
                    <th colSpan={3}>
                      <h5 className="text-center">Outcome</h5>
                    </th>
                  </tr>
                  <tr>
                    <th><h6 className="push-top-1">Age</h6></th>
                    <th><h6 className="push-top-1">Ethnicity</h6></th>
                    <th><h6 className="push-top-1">Size</h6></th>
                    <th><h6 className="push-top-1">Grade</h6></th>
                    <th><h6 className="push-top-1">ER</h6></th>
                    <th><h6 className="push-top-1">PR</h6></th>
                    <th><h6 className="push-top-1">HER2</h6></th>
                    <th><h6 className="push-top-1">Lat</h6></th>
                    <th><h6 className="push-top-1">Site</h6></th>
                    <th><h6 className="push-top-1">Type</h6></th>
                    <th className={s.borderRight}><h6 className="push-top-1">+Nodes</h6></th>

                    <th><h6 className="push-top-1">Surgery</h6></th>
                    <th><h6 className="push-top-1">Chemo</h6></th>
                    <th className={s.borderRight}><h6 className="push-top-1">Radiation</h6></th>

                    <th><h6 className="push-top-1">Year Dx</h6></th>
                    <th><h6 className="push-top-1">Status</h6></th>
                  </tr>
                  </thead>
                  <tbody>
                  {similarDiagnoses.similar_diagnosis && similarDiagnoses.similar_diagnosis.map((item, i) =>
                    <tr key={i}>
                      <td>{item['Age']}</td>
                      <td>{item['Race_group']}</td>
                      <td>{item['T_size']}</td>
                      <td>{item['Grade']}</td>
                      <td>{item['ER_status']}</td>
                      <td>{item['PR_status']}</td>
                      <td>{item['HER2_Status']}</td>
                      <td>{item['Laterality']}</td>
                      <td>{item['Primary_site']}</td>
                      <td>{item['Type']}</td>
                      <td className={s.borderRight}>{item['Nodes_Pos']}</td>

                      <td>{item['Surgery']}</td>
                      <td>{item['Chemo']}</td>
                      <td className={s.borderRight}>{item['Radiation']}</td>

                      <td>{item['Year_dx']}</td>
                      <td>{item['COD to site recode']}</td>
                    </tr>
                  )}
                  </tbody>
                </table>
                {isNil(similarDiagnoses.similar_diagnosis) && <Spin spinning/>}
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

const mapDispatch = {}

export default connect(mapState, mapDispatch)(withStyles(s)(SimilarDiagnoses))
