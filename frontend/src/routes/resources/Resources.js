import React from 'react'
import {connect} from 'react-redux'
import withStyles from 'isomorphic-style-loader/lib/withStyles'
import s from './Resources.scss'
import {Spin, Row, Col} from '../../components'
import isEmpty from 'lodash/isEmpty'

class Resources extends React.Component {
  render() {
    const {resources} = this.props
    return (
      <div className='container container-full'>
        {!isEmpty(resources) ? (
          <React.Fragment>
            <Row type='flex' gutter={16}>
              <Col xs={24} md={12} className={s.col}>
                <div className={s.card}>
                  <h2 className="push-top-2 push-bot-2">Google Links <span className="text-light">({resources.google_links.length})</span></h2>
                  <div className="custom-scroll-bar-wrapper max-height-300">
                    <div className="scrollbar-inner">
                      {resources.google_links.map(item =>
                        <div key={item} className="push-top-3">
                          <a rel='nofollow' href={item.link}>{item.title}</a>
                          <p>{item.description}</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </Col>
              <Col xs={24} md={12} className={s.col}>
                <div className={s.card}>
                  <h2 className="push-top-2 push-bot-2">Links to Pubmed Studies <span className="text-light">({resources.pubmed.length})</span>
                  </h2>
                  <div className="custom-scroll-bar-wrapper max-height-300">
                    <div className="scrollbar-inner">
                      {resources.pubmed.map(item =>
                        <div key={item} className="push-top-3">
                          <a rel='nofollow' href={item.link}>{item.title}</a>
                          <p>{item.description}</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </Col>
            </Row>
            <Row type='flex' gutter={16}>
              <Col xs={24} md={12} className={s.col}>
                <div className={s.card}>
                  <h2 className="push-top-2 push-bot-2">Blogs and Posts RegardingSimilar Cancer Diagnosis <span
                    className="text-light">({resources.blogs_and_posts.length})</span></h2>
                  <div className="custom-scroll-bar-wrapper max-height-300">
                    <div className="scrollbar-inner">
                      {resources.blogs_and_posts.map(item =>
                        <div key={item} className="push-top-3">
                          <a rel='nofollow' href={item.link}>{item.title}</a>
                          <p>{item.description}</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </Col>
              <Col xs={24} md={12} className={s.col}>
                <div className={s.card}>
                  <h2 className="push-top-2 push-bot-2">Most Recent News Articles <span
                    className="text-light">({resources.news_articles.length})</span></h2>
                  <div className="custom-scroll-bar-wrapper max-height-300">
                    <div className="scrollbar-inner">
                      {resources.news_articles.map(item =>
                        <div key={item} className="push-top-3">
                          <a rel='nofollow' href={item.link}>{item.title}</a>
                          <p>{item.description}</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </Col>
            </Row>
          </React.Fragment>
        ) : (
          <Spin spinning/>
        )}
      </div>
    )
  }
}

const mapState = state => ({
  ...state.diagnosis,
})

const mapDispatch = {}

export default connect(mapState, mapDispatch)(withStyles(s)(Resources))
