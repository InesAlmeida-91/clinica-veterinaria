-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Tempo de geração: 27-Mar-2026 às 15:02
-- Versão do servidor: 10.4.32-MariaDB
-- versão do PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Banco de dados: `clinica_veterinaria`
--

-- --------------------------------------------------------

--
-- Estrutura da tabela `animais`
--

CREATE TABLE `animais` (
  `id_animal` int(11) NOT NULL,
  `nome` varchar(100) NOT NULL,
  `especie` varchar(50) NOT NULL,
  `raca` varchar(50) DEFAULT NULL,
  `data_nascimento` date DEFAULT NULL,
  `id_dono` int(11) NOT NULL,
  `ativo` tinyint(4) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Extraindo dados da tabela `animais`
--

INSERT INTO `animais` (`id_animal`, `nome`, `especie`, `raca`, `data_nascimento`, `id_dono`, `ativo`) VALUES
(1, 'Rex', 'Cão', 'Labrador', '2020-03-10', 1, 0),
(2, 'Mimi', 'Gato', 'Siamês', '2019-07-22', 1, 1),
(3, 'Thor', 'Cão', 'Pastor Alemão', '2018-11-05', 2, 1),
(4, 'Luna', 'Gato', 'Europeu', '2021-01-15', 3, 1),
(5, 'Bobby', 'Cão', 'Beagle', '2017-09-30', 4, 1),
(7, 'coockie', 'gato', 'sem raça', '2019-06-19', 4, 1);

-- --------------------------------------------------------

--
-- Estrutura da tabela `consultas`
--

CREATE TABLE `consultas` (
  `id_consulta` int(11) NOT NULL,
  `data_consulta` datetime NOT NULL,
  `motivo` varchar(255) NOT NULL,
  `id_animal` int(11) NOT NULL,
  `id_vet` int(11) NOT NULL,
  `descricao` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Extraindo dados da tabela `consultas`
--

INSERT INTO `consultas` (`id_consulta`, `data_consulta`, `motivo`, `id_animal`, `id_vet`, `descricao`) VALUES
(1, '2026-01-10 10:00:00', 'Vacinação anual', 1, 1, NULL),
(2, '2026-01-11 11:30:00', 'Desparasitação interna', 2, 2, NULL),
(3, '2026-01-12 09:00:00', 'Consulta de rotina', 3, 5, NULL),
(4, '2026-01-13 15:00:00', 'Cirurgia ortopédica', 1, 3, NULL),
(5, '2026-01-14 16:30:00', 'Consulta de tosse', 5, 5, NULL),
(7, '2026-05-25 10:00:00', 'vacinas', 2, 2, NULL);

-- --------------------------------------------------------

--
-- Estrutura da tabela `consulta_tratamento`
--

CREATE TABLE `consulta_tratamento` (
  `id_consulta` int(11) NOT NULL,
  `id_tratamento` int(11) NOT NULL,
  `quantidade` int(11) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Extraindo dados da tabela `consulta_tratamento`
--

INSERT INTO `consulta_tratamento` (`id_consulta`, `id_tratamento`, `quantidade`) VALUES
(1, 1, 1),
(1, 2, 1),
(2, 2, 1),
(3, 3, 1),
(4, 4, 1),
(5, 3, 1),
(7, 1, 1);

-- --------------------------------------------------------

--
-- Estrutura da tabela `donos`
--

CREATE TABLE `donos` (
  `id_dono` int(11) NOT NULL,
  `nome` varchar(100) NOT NULL,
  `nif` char(9) DEFAULT NULL,
  `telefone` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `ativo` tinyint(4) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Extraindo dados da tabela `donos`
--

INSERT INTO `donos` (`id_dono`, `nome`, `nif`, `telefone`, `email`, `ativo`) VALUES
(1, 'Ana Silva', '123456789', '912345678', 'ana.silva@example.com', 1),
(2, 'Bruno Costa', '234567891', '913456789', 'bruno.costa@example.com', 1),
(3, 'Carla Rocha', '345678912', '914567890', 'carla.rocha@example.com', 1),
(4, 'Daniel Sousa', '456789123', '915678901', 'daniel.sousa@example.com', 1),
(5, 'Eva Martins', '567891234', '916789012', 'eva.martins@example.com', 1),
(6, 'Ines', '20252035', '919999999', 'ines@teste.com', 1),
(7, 'Filipe', '2569531', '963258932', 'filipe@teste.com', 1);

-- --------------------------------------------------------

--
-- Estrutura da tabela `tratamentos`
--

CREATE TABLE `tratamentos` (
  `id_tratamento` int(11) NOT NULL,
  `nome` varchar(100) NOT NULL,
  `preco` decimal(8,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Extraindo dados da tabela `tratamentos`
--

INSERT INTO `tratamentos` (`id_tratamento`, `nome`, `preco`) VALUES
(1, 'Vacina polivalente', 40.00),
(2, 'Desparasitação interna', 25.00),
(3, 'Consulta geral', 30.00),
(4, 'Cirurgia ortopédica', 300.00),
(5, 'Antibiótico', 15.00);

-- --------------------------------------------------------

--
-- Estrutura da tabela `utilizadores`
--

CREATE TABLE `utilizadores` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(20) NOT NULL,
  `ativo` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Extraindo dados da tabela `utilizadores`
--

INSERT INTO `utilizadores` (`id`, `username`, `password`, `role`, `ativo`) VALUES
(1, 'admin', 'admin123', 'admin', 1),
(2, 'rececao1', 'rececao123', 'rececao', 1),
(3, 'vet1', 'vet123', 'vet', 1);

-- --------------------------------------------------------

--
-- Estrutura da tabela `veterinarios`
--

CREATE TABLE `veterinarios` (
  `id_vet` int(11) NOT NULL,
  `nome` varchar(100) NOT NULL,
  `especialidade` varchar(100) DEFAULT NULL,
  `telefone` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Extraindo dados da tabela `veterinarios`
--

INSERT INTO `veterinarios` (`id_vet`, `nome`, `especialidade`, `telefone`) VALUES
(1, 'Dr. João Ferreira', 'Cães', '221111111'),
(2, 'Dra. Marta Lopes', 'Gatos', '222222222'),
(3, 'Dr. Pedro Almeida', 'Cirurgia', '223333333'),
(4, 'Dra. Sofia Ribeiro', 'Animais Exóticos', '224444444'),
(5, 'Dr. Luís Santos', 'Clínica Geral', '225555555');

--
-- Índices para tabelas despejadas
--

--
-- Índices para tabela `animais`
--
ALTER TABLE `animais`
  ADD PRIMARY KEY (`id_animal`),
  ADD KEY `fk_animais_donos` (`id_dono`);

--
-- Índices para tabela `consultas`
--
ALTER TABLE `consultas`
  ADD PRIMARY KEY (`id_consulta`),
  ADD KEY `fk_consultas_animais` (`id_animal`),
  ADD KEY `fk_consultas_vets` (`id_vet`);

--
-- Índices para tabela `consulta_tratamento`
--
ALTER TABLE `consulta_tratamento`
  ADD PRIMARY KEY (`id_consulta`,`id_tratamento`),
  ADD KEY `fk_ct_tratamentos` (`id_tratamento`);

--
-- Índices para tabela `donos`
--
ALTER TABLE `donos`
  ADD PRIMARY KEY (`id_dono`);

--
-- Índices para tabela `tratamentos`
--
ALTER TABLE `tratamentos`
  ADD PRIMARY KEY (`id_tratamento`);

--
-- Índices para tabela `utilizadores`
--
ALTER TABLE `utilizadores`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Índices para tabela `veterinarios`
--
ALTER TABLE `veterinarios`
  ADD PRIMARY KEY (`id_vet`);

--
-- AUTO_INCREMENT de tabelas despejadas
--

--
-- AUTO_INCREMENT de tabela `animais`
--
ALTER TABLE `animais`
  MODIFY `id_animal` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de tabela `consultas`
--
ALTER TABLE `consultas`
  MODIFY `id_consulta` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de tabela `donos`
--
ALTER TABLE `donos`
  MODIFY `id_dono` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de tabela `tratamentos`
--
ALTER TABLE `tratamentos`
  MODIFY `id_tratamento` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de tabela `utilizadores`
--
ALTER TABLE `utilizadores`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de tabela `veterinarios`
--
ALTER TABLE `veterinarios`
  MODIFY `id_vet` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Restrições para despejos de tabelas
--

--
-- Limitadores para a tabela `animais`
--
ALTER TABLE `animais`
  ADD CONSTRAINT `fk_animais_donos` FOREIGN KEY (`id_dono`) REFERENCES `donos` (`id_dono`);

--
-- Limitadores para a tabela `consultas`
--
ALTER TABLE `consultas`
  ADD CONSTRAINT `fk_consultas_animais` FOREIGN KEY (`id_animal`) REFERENCES `animais` (`id_animal`),
  ADD CONSTRAINT `fk_consultas_vets` FOREIGN KEY (`id_vet`) REFERENCES `veterinarios` (`id_vet`);

--
-- Limitadores para a tabela `consulta_tratamento`
--
ALTER TABLE `consulta_tratamento`
  ADD CONSTRAINT `fk_ct_consultas` FOREIGN KEY (`id_consulta`) REFERENCES `consultas` (`id_consulta`),
  ADD CONSTRAINT `fk_ct_tratamentos` FOREIGN KEY (`id_tratamento`) REFERENCES `tratamentos` (`id_tratamento`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
