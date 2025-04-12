pipeline {
    agent any
    
    environment {
        DB_URL = 'jdbc:postgresql://localhost:5432/forum_logs'
        DB_USER = 'admin'
        DB_PASSWORD = 'secret'
        OUTPUT_CSV = "transformed_data_${new java.text.SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date())}.csv"
    }
    
    stages {
        stage('Check Driver') {
            steps {
                script {
                    try {
                        Class.forName('org.postgresql.Driver')
                        echo "✅ PostgreSQL JDBC Driver успешно загружен"
                    } catch (Exception e) {
                        error "❌ Ошибка загрузки драйвера: ${e.message}"
                    }
                }
            }
        }
        
        stage('Test Connection') {
            steps {
                script {
                    try {
                        def conn = java.sql.DriverManager.getConnection(
                            env.DB_URL,
                            env.DB_USER,
                            env.DB_PASSWORD
                        )
                        echo "✅ Подключение к PostgreSQL успешно"
                        conn.close()
                    } catch (Exception e) {
                        error """❌ Ошибка подключения: ${e.message}
                        Проверьте:
                        1. Запущен ли контейнер (docker ps)
                        2. Параметры подключения:
                           URL: ${env.DB_URL}
                           User: ${env.DB_USER}
                        3. Настройки pg_hba.conf"""
                    }
                }
            }
        }
        
        stage('Extract Data') {
            steps {
                script {
                    try {
                        def conn = java.sql.DriverManager.getConnection(
                            env.DB_URL,
                            env.DB_USER,
                            env.DB_PASSWORD
                        )
                        
                        def query = """
                            SELECT u.user_id, 
                                   u.username, 
                                   u.created_at AS user_created,
                                   l.action_type, 
                                   l.timestamp AS action_time,
                                   l.server_response
                            FROM users u
                            JOIN logs l ON u.user_id = l.user_id
                        """
                        
                        def stmt = conn.createStatement()
                        def rs = stmt.executeQuery(query)
                        def extractedData = []
                        
                        while(rs.next()) {
                            extractedData.add([
                                user_id: rs.getInt('user_id'),
                                username: rs.getString('username'),
                                user_created: rs.getTimestamp('user_created').toString(),
                                action_type: rs.getString('action_type'),
                                action_time: rs.getTimestamp('action_time').toString(),
                                response_code: rs.getString('server_response')
                            ])
                        }
                        
                        echo "📥 Извлечено ${extractedData.size()} записей"
                        conn.close()
                        
                        // Сохраняем данные для следующего этапа
                        env.extractedData = extractedData.collect { 
                            "user_id:${it.user_id},username:${it.username},user_created:${it.user_created}," +
                            "action_type:${it.action_type},action_time:${it.action_time},response_code:${it.response_code}"
                        }.join('|')
                    } catch (Exception e) {
                        error "❌ Ошибка извлечения данных: ${e.message}"
                    }
                }
            }
        }
        
        stage('Transform Data') {
            steps {
                script {
                    try {
                        // Восстанавливаем данные из строки
                        def extractedData = env.extractedData.split('\\|').collect { entry ->
                            def map = [:]
                            entry.split(',').each { pair ->
                                def (key, value) = pair.split(':', 2) // Ограничиваем split по первому ':'
                                map[key.trim()] = value.trim()
                            }
                            return map
                        }
                        
                        // Трансформация данных
                        def transformedData = []
                        def dateFormat = new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS")
                        
                        extractedData.each { row ->
                            try {
                                // Нормализация формата даты
                                def userCreatedStr = row.user_created.replace('T', ' ').replace('Z', '')
                                def actionTimeStr = row.action_time.replace('T', ' ').replace('Z', '')
                                
                                // Парсинг дат
                                def userCreated = dateFormat.parse(userCreatedStr)
                                def actionTime = dateFormat.parse(actionTimeStr)
                                
                                // Вычисление длительности в минутах
                                def duration = (actionTime.time - userCreated.time) / (1000 * 60)
                                
                                transformedData.add([
                                    user_id: row.user_id.toInteger(),
                                    username: row.username,
                                    action_type: row.action_type,
                                    response_code: row.response_code,
                                    duration_min: Math.round(duration)
                                ])
                            } catch (Exception e) {
                                echo "⚠️ Ошибка обработки записи: ${row} - ${e.message}"
                            }
                        }
                        
                        if (transformedData.isEmpty()) {
                            error "❌ Нет данных для загрузки после трансформации"
                        }
                        
                        echo "🔄 Преобразовано ${transformedData.size()} записей"
                        env.transformedData = transformedData.collect { 
                            "user_id:${it.user_id},username:${it.username},action_type:${it.action_type}," +
                            "response_code:${it.response_code},duration_min:${it.duration_min}"
                        }.join('|')
                    } catch (Exception e) {
                        error "❌ Ошибка трансформации данных: ${e.message}"
                    }
                }
            }
        }
        
        stage('Load to CSV') {
            steps {
                script {
                    try {
                        // Восстанавливаем данные из строки
                        def transformedData = env.transformedData.split('\\|').collect { entry ->
                            def map = [:]
                            entry.split(',').each { pair ->
                                def (key, value) = pair.split(':', 2)
                                map[key.trim()] = value.trim()
                            }
                            return map
                        }
                        
                        // Создаем CSV файл
                        def csvHeader = 'user_id,username,action_type,response_code,duration_min'
                        def csvLines = transformedData.collect { row ->
                            "${row.user_id},\"${row.username}\",${row.action_type},${row.response_code},${row.duration_min}"
                        }
                        
                        writeFile file: env.OUTPUT_CSV, text: ([csvHeader] + csvLines).join('\n')
                        echo "📤 Файл ${env.OUTPUT_CSV} успешно создан"
                        archiveArtifacts artifacts: env.OUTPUT_CSV, onlyIfSuccessful: true
                    } catch (Exception e) {
                        error "❌ Ошибка записи в CSV: ${e.message}"
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo "Pipeline завершен с статусом: ${currentBuild.result}"
        }
        failure {
            echo "Сборка ${env.JOB_NAME} #${env.BUILD_NUMBER} завершилась с ошибкой"
        }
    }
    
    triggers {
        cron('0 2 * * *')
        
    }
}