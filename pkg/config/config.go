package config

import (
	"strings"

	"github.com/spf13/viper"
)

type Config struct {
	App      AppConfig      `mapstructure:"app"`
	Database DatabaseConfig `mapstructure:"database"`
}

type AppConfig struct {
	Environment  string `mapstructure:"environment"`
	Port         string `mapstructure:"port"`
	AiServiceUrl string `mapstructure:"ai_service_url"`
}

type DatabaseConfig struct {
	Host     string `mapstructure:"host"`
	Port     string `mapstructure:"port"`
	User     string `mapstructure:"user"`
	Password string `mapstructure:"password"`
	Name     string `mapstructure:"name"`
	SSLMode  string `mapstructure:"sslmode"`
}

func Load() (*Config, error) {
	viper.SetEnvPrefix("STELLAPPLY")
	viper.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))
	viper.AutomaticEnv()

	// Defaults
	viper.SetDefault("app.environment", "development")
	viper.SetDefault("app.port", "8080")
	viper.SetDefault("app.ai_service_url", "http://localhost:8000")
	viper.SetDefault("database.host", "localhost")
	viper.SetDefault("database.port", "5432")
	viper.SetDefault("database.user", "stellapply")
	viper.SetDefault("database.password", "password")
	viper.SetDefault("database.name", "stellapply")
	viper.SetDefault("database.sslmode", "disable")

	var cfg Config
	if err := viper.Unmarshal(&cfg); err != nil {
		return nil, err
	}
	return &cfg, nil
}
