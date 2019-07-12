export const formatChartNumber = (tooltipItem, data) => {
  const value = data.datasets[0].data[tooltipItem.index]
  const label = data.labels[tooltipItem.index]
  const percentage = Math.round(value * 100) / 100
  return `${label} ${percentage}%`
}

export const humanReadableNumber = (value) => {
  value = value.toString()
  value = value.split(/(?=(?:...)*$)/)
  value = value.join(',')
  return value
}

export const getAgeRangeLabel = (age) => {
  const nearestRoundedDown10 = parseInt(+age / 10, 10) * 10
  return `Ages ${nearestRoundedDown10}-${nearestRoundedDown10 + 10}`
}

export const getAverageAge = (age) => {
  const nearestRoundedDown10 = parseInt(+age / 10, 10) * 10
  return parseInt(nearestRoundedDown10 + 5)
}
