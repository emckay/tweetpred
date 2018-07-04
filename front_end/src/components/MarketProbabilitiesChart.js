import React from 'react'
import {
  HorizontalGridLines,
  VerticalBarSeries,
  XYPlot,
  XAxis,
  YAxis,
  LabelSeries,
} from 'react-vis'
import 'react-vis/dist/style.css'
import './MarketProbabilitiesChart.css'

class MarketProbabilitiesChart extends React.Component {
  state = {
    plotData: [],
    width: Math.min(window.innerWidth - 80, 520),
    height: Math.min(window.innerHeight - 70, 200),
  }
  ref = null

  static getDerivedStateFromProps(props) {
    const {bins, n} = props
    const binDistance = bins[2].start - bins[1].start
    return {
      plotData: bins.map((point, i) => ({
        x: i === 0 ? bins[1].start - binDistance : point.start,
        y: point.count / n * 100,
      })),
    }
  }

  tickFormatter = (t, i) => {
    const {bins} = this.props
    if (i === 0) {
      return `< ${bins[i].end}`
    }
    if (i === bins.length - 1) {
      return `> ${bins[bins.length - 1].start}`
    }
    return `${bins[i].start}-${bins[i].end}`
  }

  onRef = (ref) => {
    this.ref = ref
    if (this.ref) {
      const width = ref.getBoundingClientRect().width
      this.setState({width: width})
    }
  }

  render() {
    const {plotData} = this.state
    return (
      <div ref={this.onRef}>
        <XYPlot
          width={this.state.width}
          height={this.state.height}
          yDomain={[0, 100]}
        >
          <XAxis
            tickValues={plotData.map((d) => d.x)}
            tickFormat={this.tickFormatter}
          />
          <YAxis tickValues={[0, 20, 40, 60, 80, 100]} tickTotal={11} />
          <HorizontalGridLines />
          <VerticalBarSeries data={plotData} />
          <LabelSeries
            data={plotData.map((d) => ({...d, label: `${d.y.toFixed(0)}`}))}
            labelAnchorX="middle"
            labelAnchorY="text-after-edge"
          />
        </XYPlot>
      </div>
    )
  }
}

export default MarketProbabilitiesChart
