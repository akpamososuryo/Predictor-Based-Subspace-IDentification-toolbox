classdef TestPLPV < matlab.unittest.TestCase
    properties
        RepoRoot
    end

    methods (TestMethodSetup)
        function addToolboxToPath(testCase)
            testCase.RepoRoot = fileparts(fileparts(mfilename('fullpath')));
            addpath(testCase.RepoRoot);
        end
    end

    methods (TestMethodTeardown)
        function removeToolboxFromPath(testCase)
            rmpath(testCase.RepoRoot);
        end
    end

    methods (Test)
        function plpvPipelineRunsAndOutputsSane(testCase)
            % Periodic scheduling signal, small but enough repetitions
            j = 20;
            np = 15;
            N = j * np;

            [u, y, mu, ~] = testutils.makeLpvData( ...
                'N', N, 'seed', 41, 'noiseStd', 0.05, 'rhoType', 'periodic', 'period', j);

            f = 5;
            p = 10;
            n = 1;

            % Cluster periodic scheduling windows
            pind = pschedclust(mu, f, p);

            testCase.verifyNotEmpty(pind);
            % pordvarx requires at least p repetitions in a cluster
            for k = 1:size(pind,1)
                testCase.verifyGreaterThanOrEqual(length(pind{k,1}), p);
            end

            % Run PLPV preprocessor and state extraction
            % [S, Xcell, TT, Kcca] = pordvarx(u, y, mu, f, p, pind);
            
            % Use Tikhonov regularization to avoid rank-deficient LS in regress.m
            [S, Xcell, TT, Kcca] = pordvarx(u, y, mu, f, p, pind, 'tikh', 1e-2, 0);

            testCase.verifyNotEmpty(S);
            testCase.verifyNotEmpty(Xcell);
            testCase.verifyNotEmpty(TT);
            testCase.verifyNotEmpty(Kcca);
            testCase.verifyTrue(all(isfinite(S(:))), 'S contains NaN/Inf');

            % Regularized CCA solve for state sequence (use scalars to avoid CV loops)
            [Xcell2, CC] = pmodx(Xcell, TT, Kcca, n, 1e-4, 1e-8);

            testCase.verifyNotEmpty(CC);
            testCase.verifyTrue(all(isfinite(CC(:))), 'CC contains NaN/Inf');

            % Each cell should now be n-by-something and finite
            for q = 1:size(Xcell2,1)
                xq = Xcell2{q,1};
                testCase.verifySize(xq, [n size(xq,2)]);
                testCase.verifyTrue(all(isfinite(xq(:))), 'State cell contains NaN/Inf');
            end

            % Estimate PLPV matrices
            c = [0 0 1 1 0]; % allow A,B varying; force C,D constant
            [A, B, Cmat, Dmat, Kmat] = px2abcdk(Xcell2, u, y, mu, f, p, c, pind);

            testCase.verifySize(A, [1 2]);
            testCase.verifySize(B, [1 2]);
            testCase.verifySize(Cmat, [1 2]);
            testCase.verifySize(Dmat, [1 2]);
            testCase.verifySize(Kmat, [1 2]);

            testCase.verifyTrue(all(isfinite(A(:))));
            testCase.verifyTrue(all(isfinite(B(:))));
            testCase.verifyTrue(all(isfinite(Cmat(:))));
            testCase.verifyTrue(all(isfinite(Dmat(:))));
            testCase.verifyTrue(all(isfinite(Kmat(:))));
        end
    end
end