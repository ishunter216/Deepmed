import React from 'react'
import {connect} from 'react-redux'
import withStyles from 'isomorphic-style-loader/lib/withStyles'
import s from './Layout.css'
import antStyles from 'antd/lib/style/index.less'
import resetStyles from 'antd/lib/style/v2-compatible-reset.less'
import layoutStyles from 'antd/lib/layout/style/index.less'
import gridStyles from 'antd/lib/grid/style/index.less'
import buttonStyles from 'antd/lib/button/style/index.less'
import formStyles from 'antd/lib/form/style/index.less'
import inputStyles from 'antd/lib/input/style/index.less'
import inputNumberStyles from 'antd/lib/input-number/style/index.less'
import selectStyles from 'antd/lib/select/style/index.less'
import checkboxStyles from 'antd/lib/checkbox/style/index.less'
import spinStyles from 'antd/lib/spin/style/index.less'
import tableStyles from 'antd/lib/table/style/index.less'
import modalStyles from 'antd/lib/modal/style/index.less'
import alertStyles from 'antd/lib/alert/style/index.less'
import messageStyles from 'antd/lib/message/style/index.less'
import cardStyles from 'antd/lib/card/style/index.less'
import tooltipStyles from 'antd/lib/tooltip/style/index.less'
import stepsStyles from 'antd/lib/steps/style/index.less'
import progressStyles from 'antd/lib/progress/style/index.less'
import popoverStyles from 'antd/lib/popover/style/index.less'
import tabsStyles from 'antd/lib/tabs/style/index.less'
import datePickerStyles from 'antd/lib/date-picker/style/index.less'
import menuStyles from 'antd/lib/menu/style/index.less'
import radioStyles from 'antd/lib/radio/style/index.less'
import dropdownStyles from 'antd/lib/dropdown/style/index.less'
import tagStyles from 'antd/lib/tag/style/index.less'
import switchStyles from 'antd/lib/switch/style/index.less'
import {Menu, Layout, Icon, Breadcrumb,} from 'antd'

import {Link} from '../../components'
import {
  CUSTOM_ANALYTICS_ROUTE,
  DIAGNOSIS_ROUTE,
  HOME_ROUTE,
  LOGOUT_ROUTE,
  LOGIN_ROUTE,
  NATIONAL_STATES_ROUTE,
  RESOURCES_ROUTE,
  SIMILAR_DIAGNOSES_ROUTE,
  SPECIFIC_STATES_ROUTE,
  USER_ROUTE,
} from '../../routes'
import cn from 'classnames'
import {Dropdown} from 'react-bootstrap'
import RootCloseWrapper from 'react-overlays/lib/RootCloseWrapper'

/*
* TODO All html comes from another developer - refactor all html and css in project - do it in React way
* */

class CustomToggle extends React.Component {
  handleClick = (e) => {
    e.preventDefault()

    this.props.onClick(e)
  }

  render() {
    return (
      <a
        className="dropdown-toggle user-dropdown inline-block"
        id="userDropdownMenu"
        onClick={this.handleClick}
      >
        {this.props.children}
      </a>
    )
  }
}

class CustomMenu extends React.Component {
  handleRootClose = (event) => {
    this.props.onClose(event, {source: 'rootClose'})
  }

  render() {
    const {children, open, onSelect} = this.props
    return (
      <RootCloseWrapper
        disabled={!open}
        onRootClose={this.handleRootClose}
        event={'click'}
      >
        <ul className="dropdown-menu dropdown-menu-right dropdown-menu-keep-open">
          {React.Children.map(children, child => (
            React.cloneElement(child, {
              onSelect,
            })
          ))}
        </ul>
      </RootCloseWrapper>
    )
  }
}


class MenuItem extends React.Component {
  static defaultProps = {
    divider: false,
    disabled: false,
    header: false,
  }

  handleClick = (event) => {
    const {disabled, onSelect, eventKey} = this.props

    if (disabled) {
      event.preventDefault()
    }

    if (disabled) {
      return
    }

    if (onSelect) {
      onSelect(eventKey, event)
    }
  }

  render() {
    const {
      active,
      disabled,
      divider,
      header,
      onClick,
      className,
      style,
      children,
      to,
      ...props
    } = this.props
    return (
      <li
        role="presentation"
        className={cn(className, {active, disabled})}
        style={style}
      >
        <Link
          to={to}
          role="menuitem"
          tabIndex="-1"
          onClick={this.handleClick}
        >
          {children}
        </Link>
      </li>
    )
  }
}

class AppLayout extends React.Component {
  state = {
    spinnerCounter: 0,
    sidebarOpened: false,
  }

  componentDidMount() {
    this.timer = setInterval(() => {
      if (this.state.spinnerCounter === 3) {
        this.setState({
          spinnerCounter: 0
        })
      } else {
        this.setState({
          spinnerCounter: this.state.spinnerCounter + 1
        })
      }
    }, 2500)
  }

  componentWillUnmount() {
    clearInterval(this.timer)
  }

  toggleSidebarOpened = () => {
    this.setState({sidebarOpened: !this.state.sidebarOpened})
  }

  render() {
    const {currentRouteName, loading, title, loggedIn} = this.props
    const {sidebarOpened} = this.state
    const spinnerTexts = [
      'DeepMed is analyzing  over 1M patient records and treatments',
      'DeepMed is processing the most recent data available to analyze individual diagnoses',
      'DeepMed is covering actual data from hospitals and oncology clinics',
      'DeepMed covers data spanning nearly 30% of the country'
    ]

    // return (
    //   <div className="app">
    //     {loading ?
    //       <div className="page-loader">
    //         <div className="page-loader-sub-wrapper">
    //           <div className="loader-spinner">
    //             <div className="main">
    //               <div className="inside"/>
    //             </div>
    //           </div>
    //           <p className="push-top-3 text-lg" data-order="1">{spinnerTexts[this.state.spinnerCounter]}</p>
    //         </div>
    //       </div>
    //       :
    //       <div>
    //         <nav className={cn('sidebar active', sidebarOpened && 'sidebar-mobile-active')}>
    //           <div className="sidebar-header">
    //             <Link to={HOME_ROUTE}>
    //               <img src={require('../../static/deep-med-logo-new.png')} width="136" height="auto" alt="presentation"
    //                    style={{top: '15.5px'}}/>
    //             </Link>
    //           </div>
    //           {![HOME_ROUTE, LOGIN_ROUTE, USER_ROUTE].includes(currentRouteName) && (
    //             <ul className="ul-no-bullets">
    //               <li className={cn(currentRouteName === DIAGNOSIS_ROUTE && 'active')}>
    //                 <Link to={DIAGNOSIS_ROUTE}>
    //           <span className="icon-container">
    //           <i className="fa fa-heart-o"/>
    //           </span>
    //                   Diagnosis
    //                 </Link>
    //               </li>
    //               <li className={cn(currentRouteName === NATIONAL_STATES_ROUTE && 'active')}>
    //                 <Link to={NATIONAL_STATES_ROUTE}>
    //           <span className="icon-container">
    //           <i className="fa fa-bar-chart"/>
    //           </span>
    //                   National Statistics
    //                 </Link>
    //               </li>
    //               <li className={cn(currentRouteName === SPECIFIC_STATES_ROUTE && 'active')}>
    //                 <Link to={SPECIFIC_STATES_ROUTE}>
    //           <span className="icon-container">
    //           <i className="fa fa-bar-chart"/>
    //           </span>
    //                   Individual Statistics
    //                 </Link>
    //               </li>
    //               <li className={cn(currentRouteName === CUSTOM_ANALYTICS_ROUTE && 'active')}>
    //                 <Link to={CUSTOM_ANALYTICS_ROUTE}>
    //                   <span className="icon-container">
    //                     <i className="fa fa-bar-chart"/>
    //                   </span>
    //                   Custom Analytics
    //                 </Link>
    //               </li>
    //               <li
    //                 className={cn(currentRouteName === SIMILAR_DIAGNOSES_ROUTE && 'active')}>
    //                 <Link to={SIMILAR_DIAGNOSES_ROUTE}>
    //           <span className="icon-container">
    //           <i className="fa fa-files-o"/>
    //           </span>
    //                   Similar Diagnoses
    //                 </Link>
    //               </li>
    //               <li className={cn(currentRouteName === RESOURCES_ROUTE && 'active')}>
    //                 <Link to={RESOURCES_ROUTE}>
    //           <span className="icon-container">
    //           <i className="fa fa-laptop"/>
    //           </span>
    //                   Resources
    //                 </Link>
    //               </li>
    //             </ul>
    //           )}
    //         </nav>
    //
    //         <div className="main-wrapper" style={sidebarOpened ? {left: 210} : {}}>
    //           <nav className={cn('navbar navbar-fixed-top', sidebarOpened && 'has-sidebar-open')}>
    //             <a className="mobile-sidebar-trigger-container" onClick={this.toggleSidebarOpened}>
    //               {sidebarOpened ? (
    //                 <i className="icon-close-menu fa fa-times"/>
    //               ) : (
    //                 <i className="icon-open-menu fa fa-bars"/>
    //               )}
    //             </a>
    //             <div className="display-table display-table-100">
    //               <div className="display-table-cell pad-right-2">
    //                 <div className="display-table">
    //                   <div className="display-table-cell pad-right-2 hidden-md">
    //                     <img src={require('../../static/icon-logo.png')} className={s.logo}/>
    //                   </div>
    //                   <div className="display-table-cell hidden-sm">
    //                     <h1 className="no-margin" style={{lineHeight: '35px'}}>{title}</h1>
    //                   </div>
    //                 </div>
    //               </div>
    //                 <div className="display-table-cell text-right top-nav-tools">
    //                   <div className="inline-block">
    //                     <div className="display-table">
    //                       {loggedIn && (
    //                         <div className="display-table-cell">
    //                           <div className="inline-block">
    //                             <Dropdown
    //                               bsStyle='default'
    //                               id='user'
    //                             >
    //                               <CustomToggle bsRole="toggle">
    //                                 <img
    //                                   className="arrow"
    //                                   src={require('../../static/caret-down.png')}
    //                                   width="10"
    //                                   height="auto"
    //                                 />
    //                               </CustomToggle>
    //                               <CustomMenu bsRole="menu" rootCloseEvent={'click'}>
    //                                 <MenuItem to={USER_ROUTE}>Account</MenuItem>
    //                                 <MenuItem to={LOGOUT_ROUTE}>Log Out</MenuItem>
    //                               </CustomMenu>
    //                             </Dropdown>
    //                           </div>
    //                         </div>
    //                       )}
    //                     </div>
    //                   </div>
    //                 </div>
    //             </div>
    //           </nav>
    //           <div className="content-wrapper">
    //             {this.props.children}
    //           </div>
    //         </div>
    //       </div>
    //     }
    //   </div>
    // )
    return (
      <Layout style={{minHeight: '100vh'}}>
        <Layout.Header className={s.header}>
          <Link to={HOME_ROUTE} className={s.logoWrapper}>
            <img src={require('../../static/deep-med-logo-new.png')} className={s.logo}/>
          </Link>
        </Layout.Header>
        <Layout>
          <Layout.Sider width={200} style={{ background: '#fff' }}>
            <Menu
              mode="inline"
              selectedKeys={[currentRouteName]}
              style={{ height: '100%'}}
            >
              <Menu.Item key={DIAGNOSIS_ROUTE}>
                <Link to={DIAGNOSIS_ROUTE}>
                  <Icon type='heart-o' /> Diagnosis
                </Link>
              </Menu.Item>
              <Menu.Item key={NATIONAL_STATES_ROUTE}>
                <Link to={NATIONAL_STATES_ROUTE}>
                  <Icon type='area-chart' /> National Statistics
                </Link>
              </Menu.Item>
              <Menu.Item key={SPECIFIC_STATES_ROUTE}>
                <Link to={SPECIFIC_STATES_ROUTE}>
                  <Icon type='pie-chart' /> Individual Statistics
                </Link>
              </Menu.Item>
              <Menu.Item key={CUSTOM_ANALYTICS_ROUTE}>
                <Link to={CUSTOM_ANALYTICS_ROUTE}>
                  <Icon type='bar-chart' /> Custom Analytics
                </Link>
              </Menu.Item>
              <Menu.Item key={SIMILAR_DIAGNOSES_ROUTE}>
                <Link to={SIMILAR_DIAGNOSES_ROUTE}>
                  <Icon type='file' /> Similar Diagnoses
                </Link>
              </Menu.Item>
              <Menu.Item key={RESOURCES_ROUTE}>
                <Link to={RESOURCES_ROUTE}>
                  <Icon type='laptop' /> Resources
                </Link>
              </Menu.Item>
            </Menu>
          </Layout.Sider>
          <Layout style={{ padding: '0 24px 24px' }}>
            <Layout.Content>
              {this.props.children}
            </Layout.Content>
          </Layout>
        </Layout>
      </Layout>
    )
  }
}

const mapState = state => ({
  loggedIn: state.user.loggedIn,
  currentRouteName: state.global.currentRouteName,
  loading: state.diagnosis.loading,
})

const mapDispatch = {}

export default connect(mapState, mapDispatch)(withStyles(
  antStyles,
  resetStyles,
  layoutStyles,
  gridStyles,
  buttonStyles,
  formStyles,
  selectStyles,
  checkboxStyles,
  inputStyles,
  inputNumberStyles,
  tableStyles,
  spinStyles,
  modalStyles,
  alertStyles,
  messageStyles,
  cardStyles,
  tooltipStyles,
  stepsStyles,
  progressStyles,
  popoverStyles,
  tabsStyles,
  menuStyles,
  datePickerStyles,
  radioStyles,
  dropdownStyles,
  tagStyles,
  switchStyles,
  s,
)(AppLayout))
