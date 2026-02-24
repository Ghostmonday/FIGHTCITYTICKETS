'use client'

import { useEffect } from 'react'
import mixpanel from 'mixpanel-browser'
import { config } from '../../app/lib/config'

export default function Mixpanel() {
  useEffect(() => {
    if (config.mixpanelToken) {
      mixpanel.init(config.mixpanelToken, {
        debug: process.env.NODE_ENV === 'development',
        track_pageview: true,
        persistence: 'localStorage',
        ignore_dnt: true
      })
    }
  }, [])

  return null
}
