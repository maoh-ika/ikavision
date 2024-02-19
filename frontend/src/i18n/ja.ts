const lang = {
  general: {
    close: '閉じる',
    login: 'ログイン',
    buki: 'ブキ',
    main_weapon: 'メイン',
    sub_weapon: 'サブ',
    sp_weapon: 'スペシャル',
    kill: 'キル',
    death: 'デス',
    battle: 'バトル',
    rule: 'ルール',
    stage: 'ステージ',
    breakdown: '内訳',
    latestValue: '最新値',
    rocIn24h: '24h変化率',
    avePerBattle: '1試合平均',
    winRate: '勝率',
    win: 'WIN',
    lose: 'LOSE',
    rowsPerPageLabel: '1ページの行数',
    all: 'すべて',
    minutes: '分',
    seconds: '秒',
    testType: '試験版'
  },
  config: {
    matchType: '選択中の環境',
    xMatchRate: 'XPレート帯',
    allXMatchRate: '全てのレート帯を含む',
    allBattleMode: 'すべてのバトルモードを含む',
    envChangedDesc1: '表示する環境データを「',
    envChangedDesc2: '」に切り替えました。'
  },
  drawer: {
    home: 'ホーム',
    docs: 'IkaVisionについて',
    analyze: 'バトルを解析',
    battleList: 'バトル一覧',
    battleStatistics: '戦績',
    battleEnvironment: 'バトル環境',
    battleSearch: 'バトル検索',
  },
  docs: {
    about: 'IkaVisionについて',
    search: {
      title: 'バトル検索',
      conditions: '検索条件の一覧'
    }
  },
  home: {
    lead1: 'スプラトゥーン3の',
    lead2: 'バトル検索',
    lead3: 'IkaVisionは、スプラトゥーン3のバトル動画をAIで解析し、リアルなバトル環境を見るためのシステムです。',
    nonOfficial: '本サービスは任天堂株式会社とは無関係であり、任天堂によって公認またはサポートされていません。',
    allBattles: 'バトル総数',
    ranking: {
      newArrrivals: '最新の解析済みバトル',
      usageRule: '使われているブキランキング（ルール別）',
      usageStage: '使われているブキランキング（ステージ別）',
      winRateRule: 'ブキ勝率ランキング（ルール別）',
      winRateStage: 'ブキ勝率ランキング（ステージ別）',
      goBattleList: 'すべてのバトルを見る',
      goBattleSearch: 'バトルを検索する',
      goDetail: 'すべてのデータを見る'
    }
  },
  upload: {
    add: '動画ファイルを選択',
    delete: 'ファイル選択を解除',
    desc1: 'アイコンをクリック、または動画ファイルをドラッグ&ドロップ',
    desc2: '解析したいバトルを録画した動画ファイルを選択します。',
    cap1: '正常に解析するための動画の条件は',
    movieReqLink: 'こちら',
    analyze: '解析を開始',
    requesting: '解析リクエスト送信中',
    successDesc1: 'リクエストは正常に送信されました。解析の状況は',
    successDesc2: 'で確認できます。'
  },
  jobList: {
    completedTab: '解析済み',
    processingTab: '解析待ち',
    processing: {
      jobName: 'バトル動画ファイル名',
      state: '状態',
      createdAt: 'リクエスト日時',
      noData: '解析待ちのバトルはありません'
    }
  },
  statistics: {
    sammaryTab: 'まとめ',
    bukiTab: 'ブキ',
    ruleTab: 'ルール',
    stageTab: 'ステージ',
    winRate: '勝率',
    history: '履歴',
    sammary: {
      desc: 'すべてのブキ、ルール、ステージのバトルを合わせた戦績',
      allBattleCount: 'バトル数',
      winLoseCount: 'WIN/LOSEの数',
      winCount: 'WIN数',
      loseCount: 'LOSE数',
      killRate: 'キルレート',
      killAve: '平均キル',
      killTotal: 'キル総数',
      deathAve: '平均デス',
      deathTotal: 'デス総数',
      deathBreakdown: 'デス内訳',
      spAve: '平均スペシャル使用回数',
      battleCountHisotry: 'バトル数の履歴',
      winRateHistory: '勝率の履歴',
      winLoseHistory: 'WIN/LOSEの履歴',
      killAveHistory: '平均キルの履歴',
      deathAveHistory: '平均デスの履歴',
      spAveHistory: '平均スペシャル使用回数の履歴',
    },
    rateChart: {
      rateLabelX: '日付',
      winRateLabelY: '勝率(%)',
      winRateTooltipTitle: '勝率',
      winRateTotalLegend: '全バトルの勝率',
      winRateDailyLegend: 'この日のバトルの勝率',
      battleCountTotalLegend: '全バトルの合計数',
      battleCountDailyLegend: 'この日のバトル数',
      winCountTotalLegend: 'WINの総数',
      loseCountDailyLegend: 'LOSEの総数',
      KillAveTotalLegend: '全バトルの平均キル',
      KillAveDailyLegend: 'この日の平均キル',
      DeathAveTotalLegend: '全バトルの平均デス',
      DeathAveDailyLegend: 'この日の平均デス',
      SpAveTotalLegend: '全バトルの平均使用回数',
      SpAveDailyLegend: 'この日の平均使用回数',
      range1Week: '直近1週間',
      range1Month: '直近1か月',
      range3Months: '直近3か月',
      range6Months: '直近半年',
      rangeAll: '全期間',
    },
    bukiStatistics: {
      desc: 'ブキごとの戦績',
      detailTitle: 'を使ったバトルの詳細',
      descDetail: 'すべてのルール、ステージのバトルを合わせた戦績',
      bukiName: 'ブキ名',
      noData: 'ブキのバトル実績がありません',
      breakdownRule: 'ルールごとの内訳を表示',
      breakdownStage: 'ステージごとの内訳を表示',
      breakdownFaceoff: '敵として対戦したブキごとの戦績'
    },
    ruleStatistics: {
      desc: 'バトルルールごとの戦績',
      detailTitle: 'で戦ったバトルの詳細',
      descDetail: 'すべてのブキ、ステージのバトルを合わせた戦績',
      ruleName: 'ルール名',
      noData: 'ルールのバトル実績がありません',
      breakdownBuki: 'ブキごとの内訳を表示',
      breakdownStage: 'ステージごとの内訳を表示'
    },
    stageStatistics: {
      desc: 'バトルステージごとの戦績',
      detailTitle: 'で戦ったバトルの詳細',
      descDetail: 'すべてのブキ、ルールのバトルを合わせた戦績',
      stageName: 'ステージ名',
      noData: 'ステージのバトル実績がありません',
      breakdownBuki: 'ブキごとの内訳を表示',
      breakdownRule: 'ルールごとの内訳を表示'
    }
  },
  environment: {
    battlesTab: '解析したバトル',
    usageTab: 'ブキ使用率',
    winRateTab: 'ブキ勝率',
    battles: {
      allBattles: '解析したバトル総数',
      infoAllBattles: 'バトル環境の分析のためにIkaVisionによって解析されたバトルの総数です。IkaVisionは、ライブ配信されたバトル動画のみを解析対象としています。また、偏りを避けるため、配信者自身の操作キャラクターの成績は集計から除外しています。',
      ruleBreakdown: 'ルールごとのバトル数',
      infoRuleBreakdown: 'IkaVisionによって解析されたバトルをルールごとに分類した内訳です。',
      stageBreakdown: 'ステージごとのバトル数',
      infoStageBreakdown: 'IkaVisionによって解析されたバトルをステージごとに分類した内訳です。',
      bukiBreakdown: 'ブキごとのバトル数',
      infoBukiBreakdown: 'IkaVisionによって解析されたバトルをブキごとに分類した内訳です。1回のバトルに対して、バトルで使用されたすべてのブキに+1カウントするため、この表の数字の総和は「解析したバトル総数」を上回ることにご注意ください。',
      seasonBreakdown: 'シーズンごとのバトル数',
      infoSeasonBreakdown: 'IkaVisionによって解析されたバトルをシーズンごとに分類した内訳です。',
    },
    bukiUsage: {
      descRuleBased: 'ルールごとのブキ使用率',
      infoRuleBased: '1試合でブキが使用される平均個数をルールごとに算出した値です。例として、わかばシューターのガチエリアの値が2であれば、ガチエリアのバトルでは敵味方問わず平均して2個のわかばシューターが使用されていることを表しています。',
      descStageBased: 'ステージごとのブキ使用率',
      infoStageBased: '1試合あたりにブキが使用される平均個数をステージごとに算出した値です。例として、わかばシューターのナメロウ金属の値が2であれば、ナメロウ金属でのバトルでは敵味方問わず平均して2個のわかばシューターが使用されていることを表しています。',
      descRuleStageBased: 'ルールとステージの組み合わせごとのブキ使用率',
      infoRuleStageBased: '選択したブキについて、1試合でそのブキが使用される平均個数を、ルールおよびステージの組み合わせごとに算出した値です。',
      historyTitle: '1試合あたりブキ使用率の時間変化',
      usageRate: '1試合あたりブキ使用率',
      usageHistory: '日ごとの変化を表示'
    },
    bukiWinRate: {
      descRuleBased: 'ルールごとの勝率',
      descStageBased: 'ステージごとの勝率',
      descRuleStageBased: 'ルールとステージの組み合わせごとの勝率',
      infoRuleStageBased: '選択したブキについて、1試合でそのブキが使用される平均個数を、ルールおよびステージの組み合わせごとに算出した値です。',
      historyTitle: '1試合あたりブキ使用率の時間変化',
      usageRate: '1試合あたりブキ使用率',
      rateHistory: '日ごとの変化を表示'
    }
  },
  search: {
    add: '検索条件を追加',
    clear: '条件をクリア',
    search: '検索',
    resultCount: 'ヒット件数:',
    notFound: '条件に合ったバトルが見つかりませんでした',
    condition: {
      condition: '条件',
      help1: '検索条件の説明は',
      help2: 'こちら',
      gte: '以上',
      lte: '以下',
      gteDate: 'から',
      lteDate: 'まで',
      any: 'どれか',
      main_weapon: 'メインウェポン',
      sub_weapon: 'サブウェポン',
      sp_weapon: 'スペシャルウェポン',
      battleResult: {
        prefix: 'バトルの勝敗が',
        postfix: '',
        desc: 'バトルの勝敗'
      },
      battleRule: {
        prefix: 'ルールが',
        postfix: '',
        desc: 'ルール'
      },
      battleStage: {
        prefix: 'ステージが',
        postfix: '',
        desc: 'ステージ'
      },
      battleDate: {
        prefix: 'バトルの日付が',
        postfix: '',
        desc: 'バトルの日付'
      },
      deathCount: {
        prefix: 'デス数が',
        postfix: '',
        desc: 'デス数'
      },
      deathReason: {
        prefix: '',
        middlefix: 'の',
        postfix: 'でたおされた',
        desc: 'デスした理由'
      },
      deathReasonType: {
        prefix: '',
        postfix: '',
        desc: ''
      },
      deathKillerName: {
        prefix: '',
        postfix: 'にキルされた',
        desc: 'キルされた敵プレイヤー名'
      },
      deathTime: {
        prefix: 'バトル開始から',
        postfix: 'の時間帯でデスした',
        desc: 'デスした時間帯'
      },
      enemy: {
        prefix: '敵チームのプレイヤーに',
        postfix: 'がいる',
        desc: '敵チームにいるプレイヤー名'
      },
      mainPlayerBukiMain: {
        prefix: '操作キャラのメインブキが',
        postfix: '',
        desc: '操作キャラのメインブキ'
      },
      mainPlayerBukiSub: {
        prefix: '操作キャラのサブウェポンが',
        postfix: '',
        desc: '操作キャラのサブウェポン'
      },
      mainPlayerBukiSp: {
        prefix: '操作キャラのスペシャルが',
        postfix: '',
        desc: '操作キャラのスペシャル'
      },
      enemyBukiMain: {
        prefix: '敵チームのメインブキに',
        postfix: 'が含まれる',
        desc: '敵のメインブキ編成'
      },
      enemyBukiSub: {
        prefix: '敵チームのサブウェポンに',
        postfix: 'が含まれる',
        desc: '敵のサブウェポン編成'
      },
      enemyBukiSp: {
        prefix: '敵チームのスペシャルに',
        postfix: 'が含まれる',
        desc: '敵のスペシャル編成'
      },
      killCount: {
        prefix: 'キル数が',
        postfix: '',
        desc: 'キル数'
      },
      killDeadName: {
        prefix: '',
        postfix: 'をたおした',
        desc: 'キルした敵プレイヤー名'
      },
      killTime: {
        prefix: 'バトル開始から',
        postfix: 'の時間帯でキルした',
        desc: 'キルした時間帯'
      },
      matchRate: {
        prefix: 'XPが',
        postfix: 'のレート帯',
        desc: 'XPのレート帯'
      },
      matchType: {
        prefix: 'バトルモードが',
        postfix: '',
        desc: 'バトルモード'
      },
      spCount: {
        prefix: 'バトル中にスペシャルを',
        postfix: '回使用した',
        desc: 'スペシャル使用回数'
      },
      team: {
        prefix: '味方チームのプレイヤーに',
        postfix: 'がいる',
        desc: '味方チームにいるプレイヤー名'
      },
      teamBukiMain: {
        prefix: '味方チームのメインブキに',
        postfix: 'が含まれる',
        desc: '味方のメインブキ編成'
      },
      teamBukiSub: {
        prefix: '味方チームのサブウェポンに',
        postfix: '',
        desc: '味方のサブウェポン編成'
      },
      teamBukiSp: {
        prefix: '味方チームのスペシャルに',
        postfix: 'が含まれる',
        desc: '味方のスペシャル編成'
      },
    }
  },
  viewer: {
    battleInfoTab: 'バトル情報',
    analysisViewerTab: '解析結果',
    battleEdit: '修正',
    battleDate: 'バトルの日付',
    result: 'リザルト',
    count: 'カウント',
    playerName: 'プレイヤー名',
    spTrriger: 'スペシャル',
    analysisFailed: '解析失敗',
    youtube: 'YouTubeで見る',
    pinable: {
      pin: '右下に固定',
      unpin: '固定解除',
      edit: '配置とサイズを変更',
      editEnd: '配置とサイズを固定'
    },
    options: {
      movieSync: '動画の再生位置と同期'
    },
    movie: {
      title: 'バトル動画',
      playOnlyBattlePart: '解析対象のバトルのみを再生'
    },
    inkLevel: {
      title: 'インク残量',
      labelX: '時間',
      labelY: 'インク残量(%)',
      subWeaponInk: 'サブウェポンの消費インク量を表示',
      mainWeaponLegend: 'インク残量',
      subWeaponLegend: 'サブインク消費量'
    },
    playerMumberBalance: {
      title: '人数有利・不利',
      labelX: '時間',
      labelY: '人数差分',
      even: '拮抗期間',
      advantage: '有利期間',
      disadvantage: '不利期間',
      number: '人数差分',
    },
    battleCount: {
      titleGachi: 'カウント推移',
      titleNawabari: '塗りポイント推移',
      labelX: '時間',
      labelYGachi: 'カウント',
      labelYNawabari: '塗りポイント',
      teamLegend: '味方カウント',
      enemyLegend: '敵カウント'
    },
    death: {
      title: 'プレイヤーごとのデスタイミング',
      labelX: '時間',
      labelY: 'プレイヤー名',
      teamLegend: '味方デス',
      enemyLegend: '敵デス'
    },
    special: {
      title: 'プレイヤーごとのスペシャル使用タイミング',
      labelX: '時間',
      labelY: 'プレイヤー名',
      chargeLegend: 'フルチャージ',
      triggerLegend: 'SP使用',
      spoilLegend: 'SP抱え落ち',
      showFullcharge: 'フルチャージの時点を表示',
      showTrigger: 'SP使用の時点を表示',
      showSpoil: 'SP抱え落ちの時点を表示',
    },
    menu: {
      deathEventEnabled: '自分のデスを表示'
    }
  },
  battleRule: {
    nawabari: 'ナワバリバトル',
    area: 'ガチエリア',
    yagura: 'ガチヤグラ',
    hoko: 'ガチホコ',
    asari: 'ガチアサリ',
    unknown: '不明'
  },
  battleStage: {
    amabi: '海女美術大学',
    cyouzame: 'チョウザメ造船',
    gonzui: 'ゴンズイ地区',
    hirame: 'ヒラメが丘団地',
    kinmedai: 'キンメダイ美術館',
    konbu: 'コンブトラック',
    kusaya: 'クサヤ温泉',
    mahimahi: 'マヒマヒリゾート&スパ',
    mantamaria: 'マンタマリア号',
    masaba: 'マサバ海峡大橋',
    mategai: 'マテガイ放水路',
    namerou: 'ナメロウ金属',
    nampula: 'ナンプラー遺跡',
    sumeshi: 'スメーシーワールド',
    taraport: 'タラポートショッピングパーク',
    yagara: 'ヤガラ市場',
    yunohana: 'ユノハナ大渓谷',
    zatou: 'ザトウマーケット',
    takaashi: 'タカアシ経済特区',
    ohyou: 'オヒョウ海運',
    bangaitei: 'バンガイ亭',
    negitoro: 'ネギトロ炭鉱',
    map: 'マップ',
    unknown: '不明'
  },
  matchType: {
    unknown: '不明',
    regular_match: 'レギュラーマッチ',
    bankara_match: 'バンカラマッチ',
    x_match: 'Xマッチ',
    event_match: 'イベントマッチ',
    fes_match: 'フェスマッチ',
    priv_match: 'プライベートマッチ'
  },
  xRates: {
    under_1500: '1500未満',
    '1500_2000': '1500〜2000',
    '2000_2500': '2000〜2500',
    '2500_3000': '2500〜3000',
    '3000_3500': '3000〜3500',
    '3500_4000': '3500〜4000',
    upper_4000: '4000以上',
    measurement: '計測中'
  },
  buki: {
    main: {
      'unknown': '不明ブキ',
      'bold_marker': 'ボールドマーカー',
      'bold_marker_neo': 'ボールドマーカーネオ',
      'wakaba_shooter': 'わかばシューター',
      'momiji_shooter': 'もみじシューター',
      'promodeler_mg': 'プロモデラーMG',
      'promodeler_rg': 'プロモデラーRG',
      'sharp_marker': 'シャープマーカー',
      'sharp_marker_neo': 'シャープマーカーネオ',
      'spla_shooter': 'スプラシューター',
      'hero_shooter_replica': 'ヒーローシューターレプリカ',
      'spla_shooter_collabo': 'スプラシューターコラボ',
      'nzap85': 'N-ZAP85',
      'nzap89': 'N-ZAP89',
      '52gallon': '.52ガロン',
      'prime_shooter': 'プライムシューター',
      'prime_shooter_collabo': 'プライムシューターコラボ',
      '96gallon': '.96ガロン',
      '96gallon_deco': '.96ガロンデコ',
      'jet_sweeper': 'ジェットスイーパー',
      'jet_sweeper_custom': 'ジェットスイーパーカスタム',
      'space_shooter': 'スペースシューター',
      'space_shooter_collabo': 'スペースシューターコラボ',
      'l3_reelgun': 'L3リールガン',
      'l3_reelgun_d': 'L3リールガンD',
      'h3_reelgun': 'H3リールガン',
      'h3_reelgun_d': 'H3リールガンD',
      'bottole_kaiser': 'ボトルガイザー',
      'carbon_roller': 'カーボンローラー',
      'carbon_roller_deco': 'カーボンローラーデコ',
      'spla_roller': 'スプラローラー',
      'spla_roller_collabo': 'スプラローラーコラボ',
      'dynamo_roller': 'ダイナモローラー',
      'dynamo_roller_tesla': 'ダイナモローラーテスラ',
      'variable_roller': 'ヴァリアブルローラー',
      'wide_roller': 'ワイドローラー',
      'wide_roller_collabo': 'ワイドローラーコラボ',
      'classic_squiffer': 'スクイックリンα',
      'spla_charger': 'スプラチャージャー',
      'spla_scope': 'スプラスコープ',
      'spla_charger_collabo': 'スプラチャージャーコラボ',
      'spla_scope_collabo': 'スプラスコープコラボ',
      'eliter_4k': 'リッター4K',
      '4k_scope': '4Kスコープ',
      '14shiki_takedutsu_kou': '14式竹筒銃・甲',
      'soy_tuber': 'ソイチューバー',
      'soy_tuber_custom': 'ソイチューバーカスタム',
      'rpen_5h': 'R-PEN／5H',
      'nova_blaster': 'ノヴァブラスター',
      'nova_blaster_neo': 'ノヴァブラスターネオ',
      'hot_blaster': 'ホットブラスター',
      'long_blaster': 'ロングブラスター',
      'rapid_blaster': 'ラピッドブラスター',
      'rapid_blaster_deco': 'ラピッドブラスターデコ',
      'r_blaster_elite': 'Rブラスターエリート',
      'r_blaster_elite_deco': 'Rブラスターエリートデコ',
      'crash_blaster': 'クラッシュブラスター',
      'crash_blaster_neo': 'クラッシュブラスターネオ',
      'sblast92': 'S-BLAST92',
      'hissen': 'ヒッセン',
      'hissen_nouveau': 'ヒッセン・ヒュー',
      'bucket_slosher': 'バケットスロッシャー',
      'bucket_slosher_deco': 'バケットスロッシャーデコ',
      'screw_slosher': 'スクリュースロッシャー',
      'screw_slosher_neo': 'スクリュースロッシャーネオ',
      'over_flosher': 'オーバーフロッシャー',
      'over_flosher_deco': 'オーバーフロッシャーデコ',
      'explosher': 'エクスプロッシャー',
      'spla_spiner': 'スプラスピナー',
      'spla_spiner_collabo': 'スプラスピナーコラボ',
      'barrel_spiner': 'バレルスピナー',
      'barrel_spiner_deco': 'バレルスピナーデコ',
      'hydrant': 'ハイドラント',
      'kugelschreiber': 'クーゲルシュライバー',
      'kugelschreiber_nouveau': 'クーゲルシュライバー・ヒュー',
      'nautilus47': 'ノーチラス47',
      'pablo': 'パブロ',
      'pablo_nouveau': 'パブロ・ヒュー',
      'hokusai': 'ホクサイ',
      'hokusai_nouveau': 'ホクサイ・ヒュー',
      'vincent': 'フィンセント',
      'dapple_dualies': 'スパッタリー',
      'dapple_dualies_nouveau': 'スパッタリー・ヒュー',
      'spla_maneuver': 'スプラマニューバー',
      'dual_sweeper': 'デュアルスイーパー',
      'dual_sweeper_custom': 'デュアルスイーパーカスタム',
      'kelvin535': 'ケルビン525',
      'quad_hopper_black': 'クアッドホッパーブラック',
      'quad_hopper_white': 'クアッドホッパーホワイト',
      'para_shelter': 'パラシェルター',
      'para_shelter_solare': 'パラシェルターソレーラ',
      'camping_shelter': 'キャンピングシェルター',
      'camping_shelter_solare': 'キャンピングシェルターソレーラ',
      'spy_gadget': 'スパイガジェット',
      'tri_stringer': 'トライストリンガー',
      'tri_stringer_collabo': 'トライストリンガーコラボ',
      'lact450': 'LACT-450',
      'drive_wiper': 'ドライブワイパー',
      'drive_wiper_deco': 'ドライブワイパーデコ',
      'gym_wiper': 'ジムワイパー',
      'examiner': 'イグザミナー',
      'moplin': 'モップリン',
      'bottole_kaiser_foil': 'ボトルガイザーフォイル',
      'gym_wiper_nouveau': 'ジムワイパー・ヒュー',
      'hot_blaster_custom': 'ホットブラスターカスタム',
      'lact450_deco': 'LACT-450デコ',
      'rpen_5b': 'R-PEN/5B',
      'sblast91': 'S-BLAST91',
      'spla_maneuver_collabo': 'スプラマニューバーコラボ',
      'spy_gadget_solare': 'スパイガジェットソレーラ',
      'vincent_nouveau': 'フィンセント・ヒュー'
    },
    sub: {
      'unknown': '不明サブ',
      'splash_bomb': 'スプラッシュボム',
      'kyuuban_bomb': 'キューバンボム',
      'quick_bomb': 'クイックボム',
      'sprinkler': 'スプリンクラー',
      'splash_shield': 'スプラッシュシールド',
      'tansan_bomb': 'タンサンボム',
      'curling_bomb': 'カーリングボム',
      'robot_bomb': 'ロボットボム',
      'jump_beacon': 'ジャンプビーコン',
      'point_sensor': 'ポイントセンサー',
      'trap': 'トラップ',
      'poison_mist': 'ポイズンミスト',
      'line_marker': 'ラインマーカー',
      'torpede': 'トーピード'
    },
    sp: {
      'unknown': '不明SP',
      'kani_tank': 'カニタンク',
      'syoku_wonder': 'ショクワンダー',
      'kyuuinki': 'キューインキ',
      'energy_stand': 'エナジースタンド',
      'hop_sonar': 'ホップソナー',
      'same_ride': 'サメライド',
      'decoy_tirashi': 'デコイチラシ',
      'great_barrier': 'グレートバリア',
      'ultra_shoot': 'ウルトラショット',
      'megaphone_laser_51ch': 'メガホンレーザー5.1ch',
      'triple_tornade': 'トリプルトルネード',
      'teioh_ika': 'テイオウイカ',
      'multi_missile': 'マルチミサイル',
      'jet_pack': 'ジェットパック',
      'amefurashi': 'アメフラシ',
      'ultra_hanko': 'ウルトラハンコ',
      'nice_dama': 'ナイスダマ',
      'ultra_tyakuti': 'ウルトラチャクチ',
      'suminaga_sheet': 'スミナガシート'
    }
  },
  jobState: {
    created: '動画アップロード待ち',
    movieUploaded: '解析処理待ち',
    processing: '解析処理中',
    completed: '解析完了',
    failed: '解析失敗',
    cancelled: 'キャンセル',
    invalid: '不明'
  }
}

export default lang