import React from 'react'
import {RACES, REGIONS, SITES, TYPES} from '../../constants'
import messages from '../../components/messages'
import cn from 'classnames'
import {Button, Form, InputNumber, Input, Row, Select, Col} from 'antd'
import withStyles from 'isomorphic-style-loader/lib/withStyles'
import s from './DiagnosisForm.css'

class DiagnosisForm extends React.Component {
  render() {
    const {onSubmit, className} = this.props
    const {getFieldDecorator} = this.props.form

    return (
      <Form className={className} hideRequiredMark onSubmit={onSubmit}>
        <Row gutter={16}>
          <Col xs={24} sm={12}>
            <Form.Item label={'Age at Diagnosis'}>
              {getFieldDecorator('age', {
                rules: [
                  {required: true, message: messages.required},
                  {min: 18, message: messages.minAge, type: 'number'},
                ],
              })(
                <InputNumber min={18} placeholder='Type...' style={{width: '100%'}}/>
              )}
            </Form.Item>
          </Col>
          <Col xs={24} sm={12}>
            <Form.Item label={'Tumor Size in mm'}>
              {getFieldDecorator('tumor_size_in_mm', {
                rules: [
                  {required: true, message: messages.required},
                ],
              })(
                <Input placeholder='Type...'/>
              )}
            </Form.Item>
          </Col>
        </Row>
        <Row gutter={16}>
          <Col xs={24} sm={12}>
            <Form.Item label={'Tumor Grade'}>
              {getFieldDecorator('tumor_grade', {
                rules: [
                  {required: true, message: messages.required},
                ]
              })(
                <Select placeholder='Select...'>
                  <Select.Option value={1}>1 (Low)</Select.Option>
                  <Select.Option value={2}>2 (Medium)</Select.Option>
                  <Select.Option value={3}>3 (High)</Select.Option>
                </Select>
              )}
            </Form.Item>
          </Col>
          <Col xs={24} sm={12}>
            <Form.Item label={'Number of Positive Nodes'}>
              {getFieldDecorator('num_pos_nodes', {
                rules: [
                  {required: true, message: messages.required},
                ]
              })(
                <Select placeholder='Select...'>
                  {Array.from(new Array(24), (val, i) =>
                    <Select.Option key={i} value={i}>{i === 23 ? i + '+' : i}</Select.Option>
                  )}
                </Select>
              )}
            </Form.Item>
          </Col>
        </Row>
        <Row gutter={16}>
          <Col xs={24} sm={12}>
            <Form.Item label={'ER Status'}>
              {getFieldDecorator('er_status', {
                rules: [
                  {required: true, message: messages.required},
                ]
              })(
                <Select placeholder='Select...'>
                  <Select.Option value='+'>Positive</Select.Option>
                  <Select.Option value='-'>Negative</Select.Option>
                </Select>
              )}
            </Form.Item>
          </Col>
          <Col xs={24} sm={12}>
            <Form.Item label={'PR Status'}>
              {getFieldDecorator('pr_status', {
                rules: [
                  {required: true, message: messages.required},
                ]
              })(
                <Select placeholder='Select...'>
                  <Select.Option value='+'>Positive</Select.Option>
                  <Select.Option value='-'>Negative</Select.Option>
                </Select>
              )}
            </Form.Item>
          </Col>
        </Row>
        <Row gutter={16}>
          <Col xs={24} sm={12}>
            <Form.Item label={'HER2 Status'}>
              {getFieldDecorator('her2_status', {
                rules: [
                  {required: true, message: messages.required},
                ]
              })(
                <Select placeholder='Select...'>
                  <Select.Option value='+'>Positive</Select.Option>
                  <Select.Option value='-'>Negative</Select.Option>
                </Select>
              )}
            </Form.Item>
          </Col>
          <Col xs={24} sm={12}>
            <Form.Item label={'Ethnicity'}>
              {getFieldDecorator('ethnicity', {
                rules: [
                  {required: true, message: messages.required},
                ]
              })(
                <Select placeholder='Select...'>
                  {RACES.map((item, i) =>
                    <Select.Option key={i}>{item}</Select.Option>
                  )}
                </Select>
              )}
            </Form.Item>
          </Col>
        </Row>
        <Row gutter={16}>
          <Col xs={24} sm={12}>
            <Form.Item label={'Region'}>
              {getFieldDecorator('region', {
                rules: [
                  {required: true, message: messages.required},
                ]
              })(
                <Select placeholder='Select...'>
                  {REGIONS.map((item, i) =>
                    <Select.Option key={i} value={item.value}>{item.label}</Select.Option>
                  )}
                </Select>
              )}
            </Form.Item>
          </Col>
          <Col xs={24} sm={12}>
            <Form.Item label={'Laterality'}>
              {getFieldDecorator('laterality', {
                rules: [
                  {required: true, message: messages.required},
                ]
              })(
                <Select placeholder='Select...'>
                  <Select.Option value='left'>Left</Select.Option>
                  <Select.Option value='right'>Right</Select.Option>
                </Select>
              )}
            </Form.Item>
          </Col>
        </Row>
        <Row gutter={16}>
          <Col xs={24} sm={12}>
           <Form.Item label={'Site'}>
             {getFieldDecorator('site', {
               rules: [
                 {required: true, message: messages.required},
               ]
             })(
               <Select placeholder='Select...'>
                 {SITES.map((item, i) =>
                   <Select.Option key={i} value={item.value}>{item.label}</Select.Option>
                 )}
               </Select>
             )}
           </Form.Item>
          </Col>
          <Col xs={24} sm={12}>
            <Form.Item label={'Type'}>
              {getFieldDecorator('type', {
                rules: [
                  {required: true, message: messages.required},
                ]
              })(
                <Select placeholder='Select...'>
                  {TYPES.map((item, i) =>
                    <Select.Option key={i} value={item.value}>{item.label}</Select.Option>
                  )}
                </Select>
              )}
            </Form.Item>
          </Col>
        </Row>
        <Row gutter={16}>
          <Col xs={24} sm={12}>
            <Form.Item label={'Number of tumors'}>
              {getFieldDecorator('number_of_tumors', {
                rules: [
                  {required: true, message: messages.required},
                ]
              })(
                <Select placeholder='Select...'>
                  {Array.from(new Array(8), (val, i) =>
                    <Select.Option key={i} value={i}>{i}</Select.Option>
                  )}
                </Select>
              )}
            </Form.Item>
          </Col>
        </Row>
        <div style={{textAlign: 'center'}}>
          <Button type='primary' size='large' htmlType='submit'>
            Analyze
          </Button>
        </div>
      </Form>
    )
  }
}

export default Form.create()(withStyles(s)(DiagnosisForm))
